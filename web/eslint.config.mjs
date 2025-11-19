import { defineConfig, globalIgnores } from "eslint/config";
import nextVitals from "eslint-config-next/core-web-vitals";
import nextTs from "eslint-config-next/typescript";
import unusedImports from "eslint-plugin-unused-imports";

const eslintConfig = defineConfig([
    ...nextVitals,
    ...nextTs,
    // Override default ignores of eslint-config-next.
    globalIgnores([
    // Default ignores of eslint-config-next:
        ".next/**",
        "out/**",
        "build/**",
        "next-env.d.ts",
    ]),
    {
        plugins: {
            "unused-imports": unusedImports,
        },
        rules: {
            "unused-imports/no-unused-imports": "error",
            "key-spacing": ["error", { afterColon: true }],
            "indent": ["error", 4],
        },
    },
]);

export default eslintConfig;
