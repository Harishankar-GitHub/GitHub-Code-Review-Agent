# 🔄 CI/CD Integration

---

## GitHub Actions

Add this to `.github/workflows/ci.yml` in your repository:

```yaml
on:
  pull_request:

jobs:
  code-review-by-kiro-cli:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
      - name: Install Kiro CLI
        run: curl -fsSL https://kiro.dev/install.sh | sh && echo "$HOME/.kiro/bin" >> $GITHUB_PATH
      - name: Install gh-review
        run: pipx install git+https://github.com/your-org/github-code-review-agent.git
      - name: Code Review by Kiro CLI
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        run: gh-review "https://github.com/${{ github.repository }}/pull/${{ github.event.pull_request.number }}"
```

Review output appears in the Actions run log for each PR.

---

## Jenkins

1. Install on your Jenkins agent: `pipx install git+https://github.com/your-org/github-code-review-agent.git`
2. Add a `GITHUB_TOKEN` secret credential (ID: `github-token`) in **Manage Jenkins → Credentials**
3. Add this stage to your pipeline:
   ```groovy
   stage('Code Review by Kiro CLI') {
       steps {
           withCredentials([string(credentialsId: 'github-token', variable: 'GITHUB_TOKEN')]) {
               sh "gh-review ${env.CHANGE_URL}"
           }
       }
   }
   ```

Review output appears in the Jenkins build console log.
