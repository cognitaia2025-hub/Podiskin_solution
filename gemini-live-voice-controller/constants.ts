import { FunctionDeclaration, Type } from "@google/genai";
import { VoiceName } from "./types";

export const DEFAULT_SYSTEM_INSTRUCTION = `You are a helpful AI assistant integrated into a web application. 
Your goal is to assist the user by navigating the interface and filling out forms based on their voice commands.
Always be polite and confirm actions when you perform them using the tools provided.
If the user speaks Spanish, reply in Spanish.`;

export const DEFAULT_VOICE = VoiceName.Kore;

// Tool Definition: Navigate to a specific section of the app
export const NAVIGATE_TOOL: FunctionDeclaration = {
  name: 'navigate_to_section',
  description: 'Navigates the application to a specific section (dashboard, settings, or profile).',
  parameters: {
    type: Type.OBJECT,
    properties: {
      section: {
        type: Type.STRING,
        description: 'The section ID to navigate to. Valid values are: "dashboard", "settings", "profile".',
        enum: ['dashboard', 'settings', 'profile']
      },
    },
    required: ['section'],
  },
};

// Tool Definition: Fill a form field
export const FILL_FORM_TOOL: FunctionDeclaration = {
  name: 'fill_form_field',
  description: 'Fills a specific field in the user profile form with a text value.',
  parameters: {
    type: Type.OBJECT,
    properties: {
      fieldName: {
        type: Type.STRING,
        description: 'The name of the form field to update. Valid values: "firstName", "lastName", "email", "bio".',
        enum: ['firstName', 'lastName', 'email', 'bio']
      },
      value: {
        type: Type.STRING,
        description: 'The value to fill into the field.',
      },
    },
    required: ['fieldName', 'value'],
  },
};

export const TOOLS = [NAVIGATE_TOOL, FILL_FORM_TOOL];