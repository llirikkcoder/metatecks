# Playwright MCP E2E Testing Skill

**Author:** AI Office Team
**Created:** 2025-12-25
**Purpose:** Comprehensive guide for E2E testing using Playwright MCP in AI Office project

---

## Table of Contents

1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [Test Credentials](#test-credentials)
4. [Available Playwright MCP Tools](#available-playwright-mcp-tools)
5. [Common Test Patterns](#common-test-patterns)
6. [Authentication Flow](#authentication-flow)
7. [Page Testing Patterns](#page-testing-patterns)
8. [Navigation Testing](#navigation-testing)
9. [Form Testing](#form-testing)
10. [Responsive Testing](#responsive-testing)
11. [Screenshot Best Practices](#screenshot-best-practices)
12. [Error Handling](#error-handling)
13. [Troubleshooting](#troubleshooting)
14. [Complete Examples](#complete-examples)

---

## Overview

This skill provides comprehensive patterns for E2E testing the AI Office web UI using Playwright MCP tools.

**What is Playwright MCP?**
- MCP (Model Context Protocol) server providing Playwright browser automation
- Allows Claude Code to control browsers for testing
- Available tools: navigate, click, fill, screenshot, evaluate, etc.

**When to use Playwright MCP:**
- ✅ Testing web UI interactions
- ✅ Verifying page navigation
- ✅ Testing authentication flows
- ✅ Responsive design verification
- ✅ Visual regression testing (screenshots)

**When NOT to use:**
- ❌ Unit tests (use pytest)
- ❌ API endpoint testing (use requests)
- ❌ Database testing (use direct queries)
- ❌ Backend logic testing (use unit tests)

---

## Prerequisites

### 1. Frontend Server Running

```bash
cd frontend
npm run dev
```

Server should be accessible at: `http://localhost:5173`

### 2. Supabase Configured

- Database must be running
- Test user must exist
- RLS policies must be configured

### 3. Playwright MCP Server

Ensure Playwright MCP is available in Claude Code.

---

## Test Credentials

```python
BASE_URL = "http://localhost:5173"
TEST_EMAIL = "llirikk@gmail.com"
TEST_PASSWORD = "123456"
```

**Important:** These credentials must exist in Supabase database.

---

## Available Playwright MCP Tools

### Navigation
```python
mcp__playwright__playwright_navigate(
    url: str,           # URL to navigate to
    headless: bool,     # False = show browser, True = headless
    width: int,         # Viewport width (default: 1280)
    height: int,        # Viewport height (default: 720)
    timeout: int,       # Navigation timeout in ms
    waitUntil: str      # 'load', 'domcontentloaded', 'networkidle'
)
```

### Form Interaction
```python
mcp__playwright__playwright_fill(
    selector: str,      # CSS selector
    value: str          # Value to fill
)

mcp__playwright__playwright_click(
    selector: str       # CSS selector to click
)

mcp__playwright__playwright_select(
    selector: str,      # Select element selector
    value: str          # Option value to select
)

mcp__playwright__playwright_hover(
    selector: str       # Element to hover
)
```

### Screenshots
```python
mcp__playwright__playwright_screenshot(
    name: str,          # Screenshot name
    savePng: bool,      # Save as PNG file (default: False)
    storeBase64: bool,  # Return base64 (default: True)
    fullPage: bool,     # Capture full page (default: False)
    selector: str,      # Specific element to capture (optional)
    downloadsDir: str,  # Custom save directory (optional)
    width: int,         # Width in pixels (default: 800)
    height: int         # Height in pixels (default: 600)
)
```

### Page Content
```python
mcp__playwright__playwright_get_visible_text()
# Returns all visible text on the page

mcp__playwright__playwright_get_visible_html(
    cleanHtml: bool,        # Clean HTML (default: False)
    removeScripts: bool,    # Remove scripts (default: True)
    removeStyles: bool,     # Remove styles (default: False)
    removeComments: bool,   # Remove comments (default: False)
    removeMeta: bool,       # Remove meta tags (default: False)
    minify: bool,           # Minify HTML (default: False)
    maxLength: int,         # Max characters (default: 20000)
    selector: str           # Limit to specific container (optional)
)
```

### JavaScript Execution
```python
mcp__playwright__playwright_evaluate(
    script: str         # JavaScript code to execute
)
```

### Keyboard
```python
mcp__playwright__playwright_press_key(
    key: str,           # Key to press (e.g., 'Enter', 'ArrowDown')
    selector: str       # Optional: focus element first
)
```

### Console Logs
```python
mcp__playwright__playwright_console_logs(
    type: str,          # 'all', 'error', 'warning', 'log', 'info', 'debug'
    search: str,        # Search text in logs
    limit: int,         # Max logs to return
    clear: bool         # Clear after retrieval (default: False)
)
```

### Browser Control
```python
mcp__playwright__playwright_close()
# Close browser and release resources

mcp__playwright__playwright_go_back()
# Navigate back

mcp__playwright__playwright_go_forward()
# Navigate forward

mcp__playwright__playwright_resize(
    width: int,         # Viewport width
    height: int,        # Viewport height
    device: str         # Device preset (e.g., 'iPhone 13', 'iPad Pro')
)
```

---

## Common Test Patterns

### Pattern 1: Navigate and Verify

```python
# Navigate
mcp__playwright__playwright_navigate(
    url="http://localhost:5173/projects",
    headless=False
)

# Verify page loaded
text = mcp__playwright__playwright_get_visible_text()
assert "Проекты" in text or "Projects" in text

# Take screenshot
mcp__playwright__playwright_screenshot(
    name="projects_page",
    savePng=True,
    fullPage=True
)
```

### Pattern 2: Fill Form and Submit

```python
# Fill fields
mcp__playwright__playwright_fill(
    selector='input[name="email"]',
    value="llirikk@gmail.com"
)

mcp__playwright__playwright_fill(
    selector='input[name="password"]',
    value="123456"
)

# Screenshot before submit
mcp__playwright__playwright_screenshot(
    name="form_filled",
    savePng=True
)

# Submit
mcp__playwright__playwright_click(
    selector='button[type="submit"]'
)

# Wait and verify
# (add appropriate wait time)
```

### Pattern 3: Assert Text Present

```python
text = mcp__playwright__playwright_get_visible_text()

# Check multiple language variants
assert any([
    "Проекты" in text,
    "Projects" in text,
    "проекты" in text.lower()
]), "Projects page title not found"
```

### Pattern 4: Take Comparison Screenshots

```python
# Before action
mcp__playwright__playwright_screenshot(
    name="before_action",
    savePng=True
)

# Perform action
mcp__playwright__playwright_click(selector='button#toggle')

# After action
mcp__playwright__playwright_screenshot(
    name="after_action",
    savePng=True
)
```

---

## Authentication Flow

### Login Pattern

```python
def login_user(email: str, password: str):
    """Standard login flow."""
    # Navigate to login
    mcp__playwright__playwright_navigate(
        url="http://localhost:5173/login",
        headless=False
    )

    # Fill credentials
    mcp__playwright__playwright_fill(
        selector='input[type="email"]',
        value=email
    )

    mcp__playwright__playwright_fill(
        selector='input[type="password"]',
        value=password
    )

    # Screenshot before login
    mcp__playwright__playwright_screenshot(
        name="login_form_filled",
        savePng=True
    )

    # Submit
    mcp__playwright__playwright_click(
        selector='button[type="submit"]'
    )

    # Wait for navigation (add appropriate wait)
    # Verify login success
    text = mcp__playwright__playwright_get_visible_text()
    assert any([
        "Проекты" in text,
        "Projects" in text,
        "Выйти" in text,
        "Logout" in text
    ]), "Login failed - expected content not found"

    # Screenshot after login
    mcp__playwright__playwright_screenshot(
        name="after_login",
        savePng=True,
        fullPage=True
    )
```

### Logout Pattern

```python
def logout_user():
    """Standard logout flow."""
    # Click logout button
    mcp__playwright__playwright_click(
        selector='button:has-text("Выйти")'
    )

    # Verify redirected to login
    text = mcp__playwright__playwright_get_visible_text()
    assert any([
        "Вход" in text,
        "Login" in text,
        "email" in text.lower()
    ]), "Logout failed - not redirected to login"
```

---

## Page Testing Patterns

### Projects Page

```python
def test_projects_page():
    """Test projects page loads and displays correctly."""
    # Navigate
    mcp__playwright__playwright_navigate(
        url="http://localhost:5173/projects",
        headless=False
    )

    # Verify page content
    text = mcp__playwright__playwright_get_visible_text()

    # Check title
    assert "Проекты" in text or "Projects" in text

    # Check create button exists
    assert "Создать" in text or "Create" in text

    # Screenshot
    mcp__playwright__playwright_screenshot(
        name="projects_page_full",
        savePng=True,
        fullPage=True
    )
```

### Tasks Page

```python
def test_tasks_page():
    """Test tasks page loads correctly."""
    mcp__playwright__playwright_navigate(
        url="http://localhost:5173/tasks",
        headless=False
    )

    text = mcp__playwright__playwright_get_visible_text()
    assert "Задачи" in text or "Tasks" in text

    mcp__playwright__playwright_screenshot(
        name="tasks_page",
        savePng=True,
        fullPage=True
    )
```

### Admin Page

```python
def test_admin_page():
    """Test admin page access (requires admin user)."""
    mcp__playwright__playwright_navigate(
        url="http://localhost:5173/admin",
        headless=False
    )

    text = mcp__playwright__playwright_get_visible_text()

    # Check admin content
    assert any([
        "Администрирование" in text,
        "Admin" in text,
        "Пользователи" in text,
        "Users" in text
    ])

    mcp__playwright__playwright_screenshot(
        name="admin_page",
        savePng=True,
        fullPage=True
    )
```

---

## Navigation Testing

### Sidebar Navigation Pattern

```python
def test_sidebar_navigation():
    """Test navigation between pages using sidebar."""
    # Start at projects
    mcp__playwright__playwright_navigate(
        url="http://localhost:5173/projects",
        headless=False
    )

    # Click Tasks link in sidebar
    mcp__playwright__playwright_click(
        selector='a[href="/tasks"]'
    )

    # Verify on tasks page
    text = mcp__playwright__playwright_get_visible_text()
    assert "Задачи" in text or "Tasks" in text

    mcp__playwright__playwright_screenshot(
        name="navigated_to_tasks",
        savePng=True
    )

    # Navigate back to projects
    mcp__playwright__playwright_click(
        selector='a[href="/projects"]'
    )

    # Verify back on projects
    text = mcp__playwright__playwright_get_visible_text()
    assert "Проекты" in text or "Projects" in text
```

---

## Form Testing

### Create Project Pattern

```python
def test_create_project():
    """Test creating a new project."""
    # Navigate to create page
    mcp__playwright__playwright_navigate(
        url="http://localhost:5173/projects/create",
        headless=False
    )

    # Fill project name
    mcp__playwright__playwright_fill(
        selector='input[name="name"]',
        value="E2E Test Project"
    )

    # Fill project code
    mcp__playwright__playwright_fill(
        selector='input[name="code"]',
        value="E2E-TEST-001"
    )

    # Fill description
    mcp__playwright__playwright_fill(
        selector='textarea[name="description"]',
        value="Automated E2E test project created via Playwright MCP"
    )

    # Select project type
    mcp__playwright__playwright_click(
        selector='select[name="project_type"]'
    )
    mcp__playwright__playwright_click(
        selector='option[value="internal"]'
    )

    # Select priority
    mcp__playwright__playwright_click(
        selector='select[name="priority"]'
    )
    mcp__playwright__playwright_click(
        selector='option[value="medium"]'
    )

    # Screenshot form
    mcp__playwright__playwright_screenshot(
        name="project_form_filled",
        savePng=True
    )

    # Submit
    mcp__playwright__playwright_click(
        selector='button[type="submit"]'
    )

    # Verify success
    # (add appropriate wait and assertion)
```

---

## Responsive Testing

### Mobile View Pattern

```python
def test_mobile_view():
    """Test mobile responsive design."""
    # Navigate with mobile viewport
    mcp__playwright__playwright_navigate(
        url="http://localhost:5173/projects",
        headless=False,
        width=375,   # iPhone SE width
        height=667   # iPhone SE height
    )

    # Screenshot mobile view
    mcp__playwright__playwright_screenshot(
        name="projects_mobile",
        savePng=True,
        fullPage=True
    )

    # Verify content still accessible
    text = mcp__playwright__playwright_get_visible_text()
    assert "Проекты" in text or "Projects" in text
```

### Tablet View Pattern

```python
def test_tablet_view():
    """Test tablet responsive design."""
    mcp__playwright__playwright_navigate(
        url="http://localhost:5173/projects",
        headless=False,
        width=768,   # iPad width
        height=1024  # iPad height
    )

    mcp__playwright__playwright_screenshot(
        name="projects_tablet",
        savePng=True,
        fullPage=True
    )
```

### Device Presets

```python
def test_iphone_view():
    """Test using device preset."""
    mcp__playwright__playwright_navigate(
        url="http://localhost:5173/projects",
        headless=False
    )

    # Resize to iPhone 13
    mcp__playwright__playwright_resize(
        device="iPhone 13"
    )

    mcp__playwright__playwright_screenshot(
        name="projects_iphone13",
        savePng=True
    )
```

---

## Screenshot Best Practices

### 1. Descriptive Names

```python
# Good
mcp__playwright__playwright_screenshot(
    name="projects_page_after_login",
    savePng=True
)

# Bad
mcp__playwright__playwright_screenshot(
    name="test1",
    savePng=True
)
```

### 2. Full Page for Context

```python
# Capture entire page for overview
mcp__playwright__playwright_screenshot(
    name="projects_page_full",
    savePng=True,
    fullPage=True
)
```

### 3. Element-Specific for Details

```python
# Capture specific element
mcp__playwright__playwright_screenshot(
    name="project_card_detail",
    savePng=True,
    selector='.project-card:first-child'
)
```

### 4. Before/After Comparisons

```python
# Before action
mcp__playwright__playwright_screenshot(
    name="before_delete_project",
    savePng=True
)

# Perform action
mcp__playwright__playwright_click(
    selector='button.delete-project'
)

# After action
mcp__playwright__playwright_screenshot(
    name="after_delete_project",
    savePng=True
)
```

---

## Error Handling

### Handling Missing Elements

```python
try:
    mcp__playwright__playwright_click(
        selector='button.might-not-exist'
    )
except Exception as e:
    # Take screenshot of error state
    mcp__playwright__playwright_screenshot(
        name="error_element_not_found",
        savePng=True
    )

    # Log page content for debugging
    text = mcp__playwright__playwright_get_visible_text()
    print(f"Page content: {text[:500]}...")

    raise
```

### Checking Console for Errors

```python
# Check for JavaScript errors
logs = mcp__playwright__playwright_console_logs(
    type="error"
)

if logs:
    print(f"Console errors found: {logs}")
    mcp__playwright__playwright_screenshot(
        name="page_with_console_errors",
        savePng=True
    )
```

---

## Troubleshooting

### Issue: Selector Not Found

**Symptoms:**
```
Error: Selector 'button[type="submit"]' not found
```

**Solutions:**
1. Inspect DOM with browser DevTools
2. Try alternative selectors:
   ```python
   # Try multiple selectors
   selectors = [
       'button[type="submit"]',
       'button:has-text("Войти")',
       'button:has-text("Login")',
       '.submit-button'
   ]
   ```

3. Take screenshot to see page state:
   ```python
   mcp__playwright__playwright_screenshot(
       name="debug_selector_not_found",
       savePng=True
   )
   ```

4. Check page HTML:
   ```python
   html = mcp__playwright__playwright_get_visible_html()
   print(html)
   ```

### Issue: Page Not Loading

**Solutions:**
1. Increase timeout:
   ```python
   mcp__playwright__playwright_navigate(
       url="http://localhost:5173/projects",
       timeout=10000  # 10 seconds
   )
   ```

2. Use different waitUntil:
   ```python
   mcp__playwright__playwright_navigate(
       url="http://localhost:5173/projects",
       waitUntil="domcontentloaded"  # Don't wait for all resources
   )
   ```

3. Check frontend is running:
   ```bash
   curl http://localhost:5173
   ```

### Issue: Element Not Clickable

**Solutions:**
1. Scroll to element first:
   ```python
   mcp__playwright__playwright_evaluate(
       script="document.querySelector('button').scrollIntoView()"
   )
   mcp__playwright__playwright_click(selector='button')
   ```

2. Wait before clicking:
   ```python
   import time
   time.sleep(1)
   mcp__playwright__playwright_click(selector='button')
   ```

3. Use hover before click:
   ```python
   mcp__playwright__playwright_hover(selector='button')
   mcp__playwright__playwright_click(selector='button')
   ```

---

## Complete Examples

### Complete Login Test

```python
def complete_login_test():
    """Complete login test with error handling and screenshots."""
    try:
        # Navigate to login
        print("Navigating to login page...")
        mcp__playwright__playwright_navigate(
            url="http://localhost:5173/login",
            headless=False
        )

        # Screenshot login page
        mcp__playwright__playwright_screenshot(
            name="01_login_page",
            savePng=True,
            fullPage=True
        )

        # Fill email
        print("Filling email...")
        mcp__playwright__playwright_fill(
            selector='input[type="email"]',
            value="llirikk@gmail.com"
        )

        # Fill password
        print("Filling password...")
        mcp__playwright__playwright_fill(
            selector='input[type="password"]',
            value="123456"
        )

        # Screenshot filled form
        mcp__playwright__playwright_screenshot(
            name="02_login_form_filled",
            savePng=True
        )

        # Submit
        print("Submitting login form...")
        mcp__playwright__playwright_click(
            selector='button[type="submit"]'
        )

        # Wait for navigation
        import time
        time.sleep(2)

        # Verify login success
        print("Verifying login success...")
        text = mcp__playwright__playwright_get_visible_text()

        assert any([
            "Проекты" in text,
            "Projects" in text,
            "Выйти" in text
        ]), f"Login verification failed. Page content: {text[:200]}"

        # Screenshot after login
        mcp__playwright__playwright_screenshot(
            name="03_after_login_success",
            savePng=True,
            fullPage=True
        )

        print("✅ Login test passed!")

    except Exception as e:
        print(f"❌ Login test failed: {e}")

        # Error screenshot
        mcp__playwright__playwright_screenshot(
            name="ERROR_login_test",
            savePng=True,
            fullPage=True
        )

        # Check console errors
        logs = mcp__playwright__playwright_console_logs(type="error")
        if logs:
            print(f"Console errors: {logs}")

        raise

    finally:
        # Always close browser
        print("Closing browser...")
        mcp__playwright__playwright_close()
```

### Complete Project Creation Test

```python
def complete_create_project_test():
    """Complete project creation test with full flow."""
    try:
        # Login first
        complete_login_test()

        # Navigate to create page
        print("Navigating to project creation page...")
        mcp__playwright__playwright_navigate(
            url="http://localhost:5173/projects/create",
            headless=False
        )

        mcp__playwright__playwright_screenshot(
            name="01_create_project_page",
            savePng=True,
            fullPage=True
        )

        # Fill form
        print("Filling project form...")
        mcp__playwright__playwright_fill(
            selector='input[name="name"]',
            value="E2E Test Project"
        )

        mcp__playwright__playwright_fill(
            selector='input[name="code"]',
            value="E2E-TEST-001"
        )

        mcp__playwright__playwright_fill(
            selector='textarea[name="description"]',
            value="Automated E2E test project"
        )

        # Select dropdowns
        print("Selecting project type and priority...")
        mcp__playwright__playwright_click(
            selector='select[name="project_type"]'
        )
        mcp__playwright__playwright_click(
            selector='option[value="internal"]'
        )

        mcp__playwright__playwright_click(
            selector='select[name="priority"]'
        )
        mcp__playwright__playwright_click(
            selector='option[value="medium"]'
        )

        # Screenshot filled form
        mcp__playwright__playwright_screenshot(
            name="02_project_form_filled",
            savePng=True
        )

        # Submit
        print("Submitting project form...")
        mcp__playwright__playwright_click(
            selector='button[type="submit"]'
        )

        # Wait for creation
        import time
        time.sleep(2)

        # Verify success
        text = mcp__playwright__playwright_get_visible_text()
        assert "E2E Test Project" in text or "успешно" in text.lower()

        mcp__playwright__playwright_screenshot(
            name="03_project_created_success",
            savePng=True,
            fullPage=True
        )

        print("✅ Project creation test passed!")

    except Exception as e:
        print(f"❌ Project creation test failed: {e}")
        mcp__playwright__playwright_screenshot(
            name="ERROR_create_project_test",
            savePng=True,
            fullPage=True
        )
        raise

    finally:
        mcp__playwright__playwright_close()
```

---

## Summary

This skill provides:

✅ **Complete Playwright MCP tool reference**
✅ **Common testing patterns**
✅ **Authentication flows**
✅ **Page-specific test patterns**
✅ **Responsive testing approaches**
✅ **Screenshot best practices**
✅ **Error handling strategies**
✅ **Troubleshooting guide**
✅ **Complete working examples**

Use this skill as a reference when writing or debugging E2E tests for AI Office web UI.

---

**Last Updated:** 2025-12-25
**Test Environment:** http://localhost:5173
**Test User:** llirikk@gmail.com / 123456
