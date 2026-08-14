export type Question = {
  type: "MCQ" | "True / False" | "Short Answer";
  question: string;
  options: string[];
  answer: string;
  explanation: string;
  keywords: string[];
};

export type User = {
  id: number;
  name: string;
  email: string;
};
