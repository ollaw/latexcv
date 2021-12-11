## Infrastructure as a Code

The `CloudFormation Stack` contained in `template.yml` describes the AWS CI/CD Infrastructure to automate che creation of CVs in PDF format (from `.tex`).

The stack contains:
- one `CodeCommit` repository
- one `CodeBuild` project
- two `S3 Buckets`:
    - one `S3 Buckets` to store pipeline's log and artifacts
    - one `S3 Buckets` to store public pipeline artifact
- one `EventBridge Rule` to trigger the build on project change