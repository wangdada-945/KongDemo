const { defineConfig } = require("cypress");

module.exports = defineConfig({
  // JUnit for CI dashboards + GitHub Actions artifacts
  reporter: "cypress-multi-reporters",
  reporterOptions: {
    reporterEnabled: "spec, mocha-junit-reporter",
    mochaJunitReporterReporterOptions: {
      mochaFile: "cypress/results/junit-[hash].xml",
      toConsole: false,
    },
  },
  e2e: {
    baseUrl: process.env.CYPRESS_BASE_URL || "http://localhost:8002",
    supportFile: "cypress/support/e2e.js",
    specPattern: "cypress/e2e/**/*.cy.js",
  },
  video: false,
  screenshotOnRunFailure: true,
  defaultCommandTimeout: 15000,
  requestTimeout: 15000,
  env: {
    // Do not hardcode credentials. These must be provided via local env vars or CI secrets.
    KONG_USERNAME: process.env.CYPRESS_KONG_USERNAME,
    KONG_PASSWORD: process.env.CYPRESS_KONG_PASSWORD,
    KONG_ADMIN_URL: process.env.CYPRESS_KONG_ADMIN_URL || "http://localhost:8001",
  },
});

