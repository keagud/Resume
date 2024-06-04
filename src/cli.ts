import yargs from "yargs/yargs";
import { hideBin } from "yargs/helpers";

export type OutputKind = "web" | "pdf" | "all";

export interface Arguments {
  buildFormat: OutputKind;
  jobDescriptionFile?: string;
}

export async function parseBuildArgs(): Promise<Arguments> {
  let args = await yargs(hideBin(process.argv))
    .command("build [format]", "build the resume", (yargs) => {
      return yargs.positional("build", {
        describe: "Output format",
        choices: ["web", "pdf", "all"] as const,
      });
    })
    .option("desc", {
      alias: "d",
      type: "string",
      description: "insert skills from the job description",
    })
    .strictCommands()
    .parse();

  return {
    buildFormat: (args.format ?? "all") as OutputKind,
    jobDescriptionFile: args.desc,
  };
}

(async () => {
  const args = await parseBuildArgs();

  console.log(JSON.stringify(args));
})();
