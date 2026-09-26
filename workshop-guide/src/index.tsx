import { Extension, extension, type ExtensionRenderData } from "@avg-studio/sdk";
import { AuthoringGuide, type AuthoringGuideProps } from "./authoring-guide";

@extension({ id: "authoring-guide", label: "AI 创作技能 · 安装与协作指引" })
class AuthoringGuideExtension extends Extension<AuthoringGuideProps> {
  render(): ExtensionRenderData<AuthoringGuideProps> {
    return { component: AuthoringGuide, props: {} };
  }
}
export default AuthoringGuideExtension;
