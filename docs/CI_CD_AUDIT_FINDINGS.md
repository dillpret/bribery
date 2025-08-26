# CI/CD Workflow Audit Findings

*Date: 26 August 2025*

This document summarises the findings from a holistic audit of our GitHub Actions workflows and CI/CD deployment processes for the Bribery Game project. It identifies strengths, issues, and recommendations for improving our build and deployment pipeline.

## Strengths

1. **Well-structured CI/CD pipelines** with separate workflows for different purposes
2. **Proper test execution** before deployment
3. **Docker containerisation** for consistent deployment
4. **Version tagging** of Docker images
5. **Container cleanup** on deployment
6. **Proper use of GitHub Container Registry**

## Issues Identified

### 1. Windows/Linux Inconsistency
**Issue:** The GitHub Actions run tests on Windows but deploy using Linux.
- `docker-deploy.yml` uses `windows-latest` for tests but the Docker build runs on `ubuntu-latest`.
- The Python command in workflows uses `python` instead of `py -m` specified in our documentation.

**Recommendation:** 
- Update test commands to use `py -m` for consistency with our documentation and local environment.
- Consider using Python virtual environments in workflows.

### 2. Python Version Consistency
**Issue:** While our Docker uses Python 3.11, local development might use Python 3.13 based on the `__pycache__` files.

**Recommendation:**
- Ensure the CI test environment matches the Docker environment (Python 3.11).
- Add explicit Python version checks to ensure compatibility.

### 3. Oracle Cloud SSH Key Management
**Issue:** The deployment relies on SSH keys stored as GitHub secrets.

**Recommendation:**
- Document the process for rotating these keys in our deployment docs.
- Consider implementing key rotation as part of our security practices.

### 4. Nginx Configuration in Docker Setup
**Issue:** The `install-docker-oracle.sh` script sets up Nginx to proxy to port 5000, but our Docker container also exposes port 5000. This creates a double proxy situation.

**Recommendation:**
- Consider a simpler setup by having Docker directly expose port 80 to the host's port 80.
- Alternatively, keep Nginx but have the Docker container listen on a different port.

### 5. VERSION File Management
**Issue:** The version bumping is handled by `bump_version.py` but isn't integrated into our CI workflows.

**Recommendation:**
- Integrate version bumping into the CI/CD process.
- Consider automatic version increments for production deployments.

### 6. Import Path Issues
**Issue:** The `wsgi.py` file includes extensive debugging information for import errors, suggesting there have been issues with imports in production.

**Recommendation:**
- Simplify the import structure to be more predictable.
- Create a more streamlined path management approach for production vs development.

### 7. Missing GitHub Container Registry Package Linking
**Issue:** The `setup-package.yml` workflow mentions that you need to manually link the package to the repository.

**Recommendation:**
- Automate this linking if possible, or document the process clearly.
- Consider using the GitHub API to handle this linking step.

### 8. Workflow Testing Gap
**Issue:** There's no workflow to test the Docker image in an environment similar to production before deploying.

**Recommendation:**
- Add a staging deployment step to verify the Docker image works correctly.
- Implement a smoke test after deployment to verify the application is running correctly.

### 9. Oracle Cloud Deployment Variations
**Issue:** Multiple deployment scripts in the `deployment/obsolete/` directory suggest the deployment process has changed over time.

**Recommendation:**
- Consolidate deployment approaches to reduce confusion.
- Archive or remove obsolete scripts to avoid accidental use.

### 10. Requirements Management
**Issue:** Multiple requirements files (`requirements.txt`, `requirements-docker.txt`, `requirements-test.txt`, `requirements-dev.txt`) could lead to inconsistencies.

**Recommendation:**
- Establish a clearer hierarchy for these files.
- Use a tool like pip-tools to manage dependency pinning across environments.

## Security Considerations

1. **Secret Key Management**: The application uses a hardcoded fallback secret key in `app.py`. Consider implementing a more secure default.

2. **CORS Policy**: The SocketIO configuration uses `cors_allowed_origins="*"`, which may be too permissive for production.

3. **Docker Image Security**: Consider implementing security scanning for Docker images as part of the CI/CD pipeline.

## Performance Considerations

1. **Single Worker**: The Gunicorn configuration uses just one worker (`-w 1`), which may limit performance. Consider tuning this based on the available CPU resources.

2. **Build Cache**: We're already using BuildKit inline cache, which is good. Consider also implementing Docker layer caching more strategically.

## Action Items

1. **Standardise Python Commands**: Update GitHub workflow Python commands to use `py -m` for consistency with local development.

2. **Test the Complete Deployment Process**: Create a staging environment to verify the entire CI/CD pipeline.

3. **Consolidate Oracle Cloud Deployment**: Simplify and consolidate deployment scripts.

4. **Automate Version Management**: Integrate the version bumping into the CI/CD workflow.

5. **Security Hardening**: Implement security scanning and more secure defaults.

6. **Performance Tuning**: Optimise the Gunicorn configuration for better performance.

7. **Documentation Updates**: Update deployment documentation to reflect the current process.

## Next Steps

For each action item, assign an owner and deadline. Prioritise security improvements and workflow standardisation for the next sprint.
