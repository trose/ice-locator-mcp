/// <reference path="./.sst/platform/config.d.ts" />

export default $config({
  app(input) {
    return {
      name: "ice-locator-mcp",
      removal: input?.stage === "production" ? "retain" : "remove",
      home: "aws",
    };
  },
  async run() {
    // VPC for database
    const vpc = new sst.aws.Vpc("Vpc");

    // Database
    const database = new sst.aws.Postgres("Database", {
      vpc,
      databaseName: "ice_locator",
      proxy: false,
    });

    // Lambda function for heatmap API with direct URL
    const heatmapFunction = new sst.aws.Function("HeatmapApi", {
      runtime: "python3.11",
      handler: "src/ice_locator_mcp/api/lambda_handler.handler",
      link: [database],
      url: true,
    });

    // Static site for web app
    const site = new sst.aws.StaticSite("WebApp", {
      path: "web-app",
      build: {
        command: "npm run build",
        output: "dist",
      },
      environment: {
        VITE_API_URL: heatmapFunction.url,
      },
    });

    return {
      database: database.name,
      api: heatmapFunction.url,
      site: site.url,
    };
  },
});