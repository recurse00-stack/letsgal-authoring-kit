// Re-export only this extension's API from the unmodified official SDK.
// This file is used by TypeScript only; runtime imports remain @avg-studio/sdk.
export { Extension } from '../sdk/extension-module';
export type { ExtensionProps, ExtensionRenderData } from '../sdk/extension-module';
export { extension } from '../sdk/extension-decorator';
