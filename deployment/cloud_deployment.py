import os
import subprocess

class CloudDeployment:
    def __init__(self, project_name, region="us-east1"):
        self.project_name = project_name
        self.region = region

    def deploy_to_aws(self):
        """
        Deploy the bot to AWS Lambda or EC2.
        """
        try:
            print("Packaging application...")
            subprocess.run(["zip", "-r", "deployment.zip", "."], check=True)

            print("Deploying to AWS...")
            subprocess.run([
                "aws", "lambda", "create-function",
                "--function-name", self.project_name,
                "--runtime", "python3.8",
                "--role", os.getenv("AWS_LAMBDA_ROLE"),
                "--handler", "main.handler",
                "--zip-file", "fileb://deployment.zip",
                "--timeout", "300",
                "--memory-size", "512"
            ], check=True)
            print("Deployment successful.")
        except Exception as e:
            print(f"Error during AWS deployment: {e}")

    def deploy_to_gcp(self):
        """
        Deploy the bot to Google Cloud Functions.
        """
        try:
            print("Deploying to Google Cloud...")
            subprocess.run([
                "gcloud", "functions", "deploy", self.project_name,
                "--runtime", "python38",
                "--trigger-http",
                "--entry-point", "main",
                "--region", self.region
            ], check=True)
            print("Deployment successful.")
        except Exception as e:
            print(f"Error during GCP deployment: {e}")

    def deploy_to_azure(self):
        """
        Deploy the bot to Azure Functions.
        """
        try:
            print("Deploying to Azure...")
            subprocess.run([
                "az", "functionapp", "create",
                "--resource-group", os.getenv("AZURE_RESOURCE_GROUP"),
                "--consumption-plan-location", self.region,
                "--runtime", "python",
                "--name", self.project_name,
                "--storage-account", os.getenv("AZURE_STORAGE_ACCOUNT"),
                "--functions-version", "3"
            ], check=True)
            print("Deployment successful.")
        except Exception as e:
            print(f"Error during Azure deployment: {e}")

if __name__ == "__main__":
    deployment = CloudDeployment(project_name="StockBot")
    deployment.deploy_to_aws()  # Change to `deploy_to_gcp()` or `deploy_to_azure()` as needed
