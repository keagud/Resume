import OpenAI from "openai";
import { writeSync, readSync, openSync } from "fs";
import PromptSync from "prompt-sync";

import * as readline from "readline"

const openai = new OpenAI();

const MODEL_PROMPT = `
You are a resume assistant. Your task is to convert a prose job description into a list of relevant skills appropriate for use in a resume. Aim for brevity and specificity. Each item in the list should be no more than 20 characters long (e.g. "Microsoft Office" would be acceptable, but "Proficiency in word processing and spreadsheets in Microsoft Office" would be unacceptable). Do not use phrases like "understanding of X", "proficiency in X", rather just say "X".  Your response should consist of a markdown-formatted list of 10-20 items depending on the number of skills mentioned in the input. Only return the list, do not include any other commentary. 
`;



const consoleInput = PromptSync({ sigint: true });

async function extractJobSkills(description: string, isTest: boolean = false): Promise<string[]> {

  if (isTest) { return ["Alfa", "Bravo", "Charlie", "Delta", "Echo", "Hotel", "Foxtrot"] }


  const completion = await openai.chat.completions.create({
    messages: [
      { role: "system", content: MODEL_PROMPT },
      { role: "user", content: description },
    ],
    model: "gpt-4-turbo",
  });

  const response = completion.choices[0].message.content
    ?? (() => { throw "No message content"; })();

  return response
    .split('\n')
    .map(ln => ln.slice(1).trim())
    .filter(x => x)

}


function promptInspectSkills(aiResponses: string[]): string[] {

  console.log(`Found ${aiResponses.length} skills: `);
  aiResponses.forEach((x, i) => console.log(`${i + 1}. ${x}`));

  const reply = consoleInput("Input numbers to skip: ");

  const toRemove = reply.split(/\s+/).map(n => parseInt(n, 10));

  return aiResponses.map((x, i) => toRemove.includes(i + 1) ? "" : x).filter(x => x);


}

function formatSkillsResponse(response: string[]): string {
  const innerList = response
    .map((ln) => `<li>${ln}</li>`)
    .join("\n");

  return [`<ul class="skills-list">`, innerList, "</ul>"].join("\n");
}

export async function generateCustomSkillsComponent(
  description: string,
): Promise<string> {


  const aiResponses = await extractJobSkills(description);
  const filteredSkillList = promptInspectSkills(aiResponses);

  return formatSkillsResponse(filteredSkillList);

}
