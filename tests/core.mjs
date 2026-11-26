import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import { createContext, runInContext } from "node:vm";

const element = { addEventListener() {}, replaceChildren() {} };
const context = createContext({
  document: { getElementById: () => element },
  localStorage: { getItem: () => null },
  URL,
});
runInContext(await readFile(new URL("../app.js", import.meta.url), "utf8"), context);
const { readList, readFiles, fromLink } = context;
const file = (name, content) => ({ name, text: async () => content });

const followers = await readFiles([
  file("followers_1.json", '[{"string_list_data":[{"value":"Alice"}]}]'),
  file("followers_2.json", '[{"string_list_data":[{"value":"alice"}]},{"string_list_data":[{"href":"https://instagram.com/_u/Charlie/"}]}]'),
], "followers");
assert.deepEqual([...followers], ["alice", "charlie"]);

const following = await readList(file("following.json",
  '{"relationships_following":[{"title":"Bob","string_list_data":[]}]}'
), "following");
assert.deepEqual([...following], ["bob"]);

const empty = await readList(file("following.json", '{"relationships_following":[]}'), "following");
assert.deepEqual([...empty], []);
assert.equal(fromLink("https://example.org/alice"), null);
assert.equal(fromLink("javascript:alert(1)"), null);
assert.equal(fromLink(undefined), null);
await assert.rejects(readList(file("followers_1.json", '[{"string_list_data":[{}]}]'), "followers"), /export Instagram/);
await assert.rejects(readFiles([file("following.json", "[]")], "followers"), /autre liste/);
await assert.rejects(readList(file("following.json", "{"), "following"), /export Instagram/);
await assert.rejects(readList(file("following.json", '{"unrelated":[]}'), "following"), /export Instagram/);
console.log("Tests de lecture, déduplication et validation réussis.");


const exported = (name, directory) => ({ name, webkitRelativePath: directory + "/" + name });
const directory = "export/connections/followers_and_following";
const exportFiles = [
  exported("followers1.JSON", directory),
  exported("followers_2.json", directory),
  exported("following.json", directory),
  exported("close_friends.json", directory),
  exported("followers_1.html", "incomplete-export"),
  exported("following.html", "another-incomplete-export"),
];
const detected = context.groupExportFiles(exportFiles);
assert.equal(detected.length, 1);
assert.deepEqual([...detected[0].followers], exportFiles.slice(0, 2));
assert.deepEqual([...detected[0].following], [exportFiles[2]]);
assert.equal(context.groupExportFiles([
  ...exportFiles,
  exported("followers1.html", "alternative"),
  exported("following_1.htm", "alternative"),
]).length, 2);
assert.equal(context.groupExportFiles([
  exported("followers1.html", directory),
  exported("following.json", directory),
]).length, 0);
console.log("Tests de détection des dossiers d’export réussis.");
