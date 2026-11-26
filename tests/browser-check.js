"use strict";

(async () => {
    const find = (id) => document.getElementById(id);
    const put = (id, files) => {
      const selection = new DataTransfer();
      for (const [name, content] of files) selection.items.add(new File([content], name));
      find(id).files = selection.files;
      find(id).dispatchEvent(new Event("change"));
    };
    const wait = async () => {
      for (let time = 0; time < 100; time++) {
        if (!find("compare").disabled) return;
        await new Promise((resolve) => setTimeout(resolve, 20));
      }
      throw new Error("Analyse bloquée");
    };
    const accounts = () => [...find("accounts").querySelectorAll("a")].map((link) => link.textContent);
    const outcome = {};
    put("followers", [
      ["followers_1.json", JSON.stringify([{ string_list_data: [{ value: "ALICE" }] }])],
      ["followers_2.html", '<h1>Followers</h1><a href="https://www.instagram.com/_u/alice">alice</a><a href="https://instagram.com/charlie/">charlie</a><a href="https://example.org/fake">fake</a>'],
    ]);
    const following = ["alice", "bob", "dora"].map((title) => ({ title, string_list_data: [] }));
    put("following", [["following.json", JSON.stringify({ relationships_following: following })]]);
    find("compare").click();
    await wait();
    outcome.status = find("status").textContent;
    outcome.counts = ["total-followers", "total-following", "total-mutual"].map((id) => find(id).textContent);
    outcome.notBack = accounts();
    outcome.profile = find("accounts").querySelector("a")?.href;
    find("search").value = "@BO";
    find("search").dispatchEvent(new Event("input"));
    outcome.filtered = accounts();

    let captured;
    const createObjectURL = URL.createObjectURL;
    URL.createObjectURL = (blob) => { captured = blob; return createObjectURL(blob); };
    const click = HTMLAnchorElement.prototype.click;
    HTMLAnchorElement.prototype.click = () => {};
    find("export").click();
    HTMLAnchorElement.prototype.click = click;
    URL.createObjectURL = createObjectURL;
    outcome.csv = await captured.text();

    find("accounts").querySelector("button:last-child").click();
    outcome.saved = JSON.parse(localStorage.getItem("unfollowspy.ignored"));
    outcome.ignored = accounts();
    find("manage").click();
    outcome.dialog = find("ignored-dialog").open;
    find("ignored-list").querySelector("button").click();
    find("ignored-dialog").close();
    outcome.restored = accounts();
    find("search").value = "";
    find("not-followed").click();
    outcome.notFollowed = accounts();

    put("following", [["following.json", "{"]]);
    find("compare").click();
    await wait();
    outcome.invalid = find("analysis").hidden && find("status").textContent.includes("following.json");
    put("following", [["following.json", '{"relationships_following":[]}']]);
    find("compare").click();
    await wait();
    outcome.emptyValid = !find("analysis").hidden && find("total-following").textContent === "0";
    outcome.styled = getComputedStyle(document.querySelector(".files")).display === "grid";
    return outcome;
  })().then((actual) => {
  const expected = {
    status: "Comparaison terminée.",
    counts: ["2", "3", "1"],
    notBack: ["@bob", "@dora"],
    profile: "https://www.instagram.com/bob/",
    filtered: ["@bob"],
    csv: "Pseudo,Lien Instagram\r\nbob,https://www.instagram.com/bob/\r\ndora,https://www.instagram.com/dora/\r\n",
    saved: ["bob"],
    ignored: [],
    dialog: true,
    restored: ["@bob"],
    notFollowed: ["@charlie"],
    invalid: true,
    emptyValid: true,
    styled: true,
  };
  for (const [key, value] of Object.entries(expected)) {
    if (JSON.stringify(actual[key]) !== JSON.stringify(value)) {
      throw new Error(key + ": " + JSON.stringify(actual[key]));
    }
  }
  document.documentElement.dataset.browserReport = encodeURIComponent(JSON.stringify({ passed: true }));
  document.querySelector("h1").textContent = "Vérification web réussie";
}).catch((error) => {
  document.documentElement.dataset.browserReport = encodeURIComponent(JSON.stringify({ passed: false, message: error.message }));
  document.querySelector("h1").textContent = "Échec dans le navigateur : " + error.message;
});

