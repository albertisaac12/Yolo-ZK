import {testw} from "./index";

async function main() {
  const embedding = ["1", "2", "3", "4"];
  const enrolled = ["1", "2", "3", "4"];
  const commitment_hash = "0x130bf204a32cac1f0ace56c78b731aa3809f06df2731ebcf6b3464a15788b1b9"; // Used the main.ts function

  await testw(embedding, enrolled, commitment_hash);
  console.log("✅ Circuit executed successfully");
}

main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error(error);
    process.exit(1);
  });