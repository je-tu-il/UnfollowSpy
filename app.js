"use strict";

const byId = (id) => document.getElementById(id);
const profile = (name) => "https://www.instagram.com/" + name + "/";
const normalize = (value) => {
  if (typeof value !== "string") return null;
  const name = value.trim().replace(/^@/, "").toLowerCase();
  return /^[a-z0-9_.]{1,30}$/.test(name) && /[a-z0-9_]/.test(name) ? name : null;
};

function fromLink(href) {
  if (typeof href !== "string" || !/^(?:https?:\/\/|\/_u\/)/i.test(href.trim())) return null;
  try {
    const url = new URL(href, "https://www.instagram.com");
    if (!["https:", "http:"].includes(url.protocol)) return null;
    if (!["instagram.com", "www.instagram.com"].includes(url.hostname)) return null;
    return normalize(url.pathname.match(/^\/(?:_u\/)?([\w.]+)\/?$/)?.[1]);
  } catch {
    return null;
  }
}

async function readList(file, kind) {
  try {
    const source = (await file.text()).replace(/^\uFEFF/, "");
    if (/\.json$/i.test(file.name)) {
      const data = JSON.parse(source);
      const key = kind === "followers" ? "relationships_followers" : "relationships_following";
      const entries = Array.isArray(data) ? data : data?.[key];
      if (!Array.isArray(entries)) throw new Error();
      return entries.map((entry) => {
        const links = entry?.string_list_data ?? [];
        if (!Array.isArray(links)) throw new Error();
        const name = links.map((link) => normalize(link?.value) ?? fromLink(link?.href))
          .find(Boolean) ?? normalize(entry?.title);
        if (!name) throw new Error();
        return name;
      });
    }
    if (!/\.html?$/i.test(file.name)) throw new Error();
    const template = document.createElement("template");
    template.innerHTML = source;
    const names = [...template.content.querySelectorAll("a[href]")]
      .map((link) => fromLink(link.getAttribute("href"))).filter(Boolean);
    if (!names.length) {
      const heading = template.content.querySelector("h1, title")?.textContent.trim().toLowerCase();
      const headings = kind === "followers" ? ["followers", "abonnés"] : ["following", "abonnements"];
      if (!headings.includes(heading) || template.content.querySelector("a[href]")) throw new Error();
    }
    return names;
  } catch {
    throw new Error("« " + file.name + " » ne correspond pas à un export Instagram lisible pour cette liste.");
  }
}

function groupExportFiles(files) {
  const groups = new Map();
  for (const file of files) {
    const match = file.name.match(/^(followers|following)(?:_?\d+)?\.(json|html?)$/i);
    if (!match) continue;
    const kind = match[1].toLowerCase();
    const format = match[2].toLowerCase() === "json" ? "json" : "html";
    const path = file.webkitRelativePath || file.name;
    const key = path.slice(0, path.lastIndexOf("/") + 1) + "|" + format;
    if (!groups.has(key)) groups.set(key, { followers: [], following: [] });
    groups.get(key)[kind].push(file);
  }
  return [...groups.values()].filter(({ followers, following }) => followers.length && following.length);
}

async function readFiles(files, kind) {
  const unexpected = kind === "followers" ? /^following(?:[_\d]*)\./i : /^followers(?:[_\d]*)\./i;
  const names = new Set();
  for (const file of files) {
    if (unexpected.test(file.name)) throw new Error("« " + file.name + " » appartient à l’autre liste.");
    for (const name of await readList(file, kind)) names.add(name);
  }
  return names;
}

function loadIgnored() {
  try {
    return new Set(JSON.parse(localStorage.getItem("unfollowspy.ignored") ?? "[]").map(normalize).filter(Boolean));
  } catch {
    return new Set();
  }
}

const ignored = loadIgnored();
const modes = ["not-back", "not-followed"];
const pageSize = 50;
let lists = null;
let results = {};
let mode = modes[0];
let page = 0;
let feedbackTimeout;
let comparing = false;

function feedback(message) {
  const target = byId("feedback");
  clearTimeout(feedbackTimeout);
  target.textContent = message;
  target.hidden = false;
  feedbackTimeout = setTimeout(() => { target.hidden = true; }, 4000);
}

function action(label, run) {
  const button = document.createElement("button");
  button.type = "button";
  button.textContent = label;
  button.addEventListener("click", run);
  return button;
}

function saveIgnored(message) {
  try {
    localStorage.setItem("unfollowspy.ignored", JSON.stringify([...ignored]));
  } catch {
    message += " La liste restera disponible jusqu’à la fermeture de la page.";
  }
  byId("ignored-status").textContent = message;
  feedback(message);
  renderIgnored();
  if (lists) updateResults();
}

function renderIgnored() {
  byId("ignored-count").textContent = ignored.size;
  byId("ignored-list").replaceChildren(...[...ignored].sort().map((name) => {
    const row = document.createElement("li");
    const label = document.createElement("span");
    label.className = "account";
    label.textContent = "@" + name;
    row.append(label, action("Rétablir", () => {
      ignored.delete(name);
      saveIgnored("@" + name + " rétabli.");
    }));
    return row;
  }));
}

function renderAccount(name) {
  const row = document.createElement("li");
  const avatar = document.createElement("span");
  avatar.className = "avatar";
  avatar.setAttribute("aria-hidden", "true");
  avatar.textContent = name.slice(0, 2).toUpperCase();
  const link = document.createElement("a");
  link.className = "account";
  link.href = profile(name);
  link.target = "_blank";
  link.rel = "noopener noreferrer";
  link.textContent = "@" + name;
  row.append(avatar, link, action("Copier", async () => {
    try {
      await navigator.clipboard.writeText(name);
      feedback("Pseudo copié.");
    } catch {
      feedback("Copie indisponible. Vous pouvez sélectionner le pseudo.");
    }
  }), action("Ignorer", () => {
    ignored.add(name);
    saveIgnored("@" + name + " ignoré.");
  }));
  return row;
}

function renderResults() {
  const query = byId("search").value.trim().replace(/^@/, "").toLowerCase();
  const names = results[mode].filter((name) => name.includes(query));
  const pages = Math.max(1, Math.ceil(names.length / pageSize));
  page = Math.min(page, pages - 1);
  byId("accounts").replaceChildren(...names.slice(page * pageSize, (page + 1) * pageSize).map(renderAccount));
  byId("pages").hidden = pages < 2;
  byId("previous").disabled = page === 0;
  byId("next").disabled = page === pages - 1;
  byId("page").textContent = (page + 1) + " / " + pages;
  byId("empty").hidden = names.length > 0;
  byId("empty").textContent = query ? "Aucun pseudo trouvé." : "Aucun compte dans cette liste.";
  byId("export").disabled = results[mode].length === 0;
  for (const id of modes) {
    byId(id).setAttribute("aria-pressed", String(id === mode));
    byId(id).querySelector("span").textContent = results[id].length;
  }
}

function updateResults() {
  const { followers, following } = lists;
  results = {
    "not-back": [...following].filter((name) => !followers.has(name) && !ignored.has(name)).sort(),
    "not-followed": [...followers].filter((name) => !following.has(name) && !ignored.has(name)).sort(),
  };
  byId("total-followers").textContent = followers.size;
  byId("total-following").textContent = following.size;
  byId("total-mutual").textContent = [...followers].filter((name) => following.has(name)).length;
  renderResults();
}

for (const id of ["followers", "following"]) {
  byId(id).addEventListener("change", () => {
    lists = null;
    byId("analysis").hidden = true;
    byId("status").textContent = "";
    byId("folder-status").textContent = "Sélectionnez le dossier décompressé pour détecter les deux listes.";
  });
}

const folderInput = byId("export-folder");
const folderStatus = byId("folder-status");

byId("open-folder").addEventListener("click", () => {
  if (!("webkitdirectory" in folderInput)) {
    folderStatus.textContent = "Ce navigateur permet la sélection manuelle des fichiers ci-dessous.";
    return;
  }
  folderInput.click();
});

folderInput.addEventListener("change", () => {
  const groups = groupExportFiles(folderInput.files);
  folderInput.value = "";
  if (groups.length !== 1) {
    folderStatus.textContent = groups.length
      ? "Plusieurs exports détectés. Ouvrez un dossier contenant un seul export ou sélectionnez les fichiers manuellement."
      : "Aucune paire complète trouvée. Sélectionnez le dossier décompressé contenant les deux listes.";
    return;
  }

  const { followers, following } = groups[0];
  for (const [id, files] of Object.entries({ followers, following })) {
    const selection = new DataTransfer();
    files.forEach((file) => selection.items.add(file));
    const input = byId(id);
    input.files = selection.files;
    input.dispatchEvent(new Event("change"));
  }
  folderStatus.textContent = "Fichiers détectés · " + followers.length + " pour les abonnés, " + following.length + " pour les abonnements.";
});

byId("imports").addEventListener("submit", async (event) => {
  event.preventDefault();
  if (comparing) return;
  comparing = true;
  const inputs = ["followers", "following", "compare"].map(byId);
  const [followersInput, followingInput] = inputs;
  const followersFiles = [...followersInput.files];
  const followingFiles = [...followingInput.files];
  inputs.forEach((input) => { input.disabled = true; });
  byId("open-folder").disabled = true;
  byId("analysis").hidden = true;
  lists = null;
  byId("status").textContent = "Analyse en cours…";
  try {
    const [followers, following] = await Promise.all([
      readFiles(followersFiles, "followers"),
      readFiles(followingFiles, "following"),
    ]);
    lists = { followers, following };
    byId("search").value = "";
    mode = modes[0];
    page = 0;
    updateResults();
    byId("analysis").hidden = false;
    byId("status").textContent = "Comparaison terminée.";
  } catch (error) {
    byId("status").textContent = error.message;
  } finally {
    inputs.forEach((input) => { input.disabled = false; });
    byId("open-folder").disabled = false;
    comparing = false;
  }
});

for (const id of modes) {
  byId(id).addEventListener("click", () => {
    mode = id;
    page = 0;
    renderResults();
  });
}
byId("search").addEventListener("input", () => { page = 0; renderResults(); });
byId("previous").addEventListener("click", () => { page -= 1; renderResults(); });
byId("next").addEventListener("click", () => { page += 1; renderResults(); });

byId("export").addEventListener("click", () => {
  const rows = results[mode].map((name) => name + "," + profile(name));
  const csv = ["Pseudo,Lien Instagram", ...rows].join("\r\n") + "\r\n";
  const url = URL.createObjectURL(new Blob(["\uFEFF", csv], { type: "text/csv;charset=utf-8" }));
  const download = document.createElement("a");
  download.href = url;
  download.download = mode === modes[0] ? "instagram_ne_me_suivent_pas.csv" : "instagram_non_suivis_en_retour.csv";
  download.click();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
});

byId("manage").addEventListener("click", () => byId("ignored-dialog").showModal());
byId("legacy-form").addEventListener("submit", async (event) => {
  event.preventDefault();
  const input = byId("legacy");
  if (!input.files.length) return;
  try {
    const content = await input.files[0].text();
    const names = content.split(/\r?\n/).map(normalize).filter(Boolean);
    if (!names.length) throw new Error();
    const before = ignored.size;
    names.forEach((name) => ignored.add(name));
    saveIgnored((ignored.size - before) + " pseudo(s) ajouté(s).");
    event.target.reset();
  } catch {
    byId("ignored-status").textContent = "Aucun pseudo valide n’a pu être lu.";
  }
});
renderIgnored();
