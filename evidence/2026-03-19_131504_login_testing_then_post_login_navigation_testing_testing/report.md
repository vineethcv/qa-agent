# QA Report

**Flow:** login_testing -> post_login_navigation_testing
**Environment:** testing
**Status:** FAILED

## Step Results

1. FILL (email input) — PASSED
2. FILL (password input) — PASSED
3. CLICK (sign in button) — PASSED
4. SCREENSHOT — PASSED
1. ASSERT_TEXT — PASSED
2. ASSERT_TEXT — PASSED
3. ASSERT_TEXT — FAILED
   - Error: Expected text not found: FAIL_Profile

## Failures

### Step 3 — ASSERT_TEXT

**Expected:** FAIL_Profile
**Actual:** Not observed
**Error:** Expected text not found: FAIL_Profile
**Evidence:** evidence/2026-03-19_131504_login_testing_then_post_login_navigation_testing_testing/step_03_assert_text.png

## Evidence

- screenshot: evidence/2026-03-19_131504_login_testing_then_post_login_navigation_testing_testing/step_03_assert_text.png (Captured for step 3 in flow post_login_navigation_testing)

## Conclusion

The `login_testing -> post_login_navigation_testing` flow did not meet expected behavior. Review failed steps and evidence.
