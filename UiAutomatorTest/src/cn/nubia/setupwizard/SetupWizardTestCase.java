package cn.nubia.setupwizard;

import com.android.uiautomator.core.UiObject;
import com.android.uiautomator.core.UiObjectNotFoundException;
import com.android.uiautomator.core.UiScrollable;
import com.android.uiautomator.core.UiSelector;
import com.ztemt.test.automator.AutomatorTestCase;

public class SetupWizardTestCase extends AutomatorTestCase {

    public void testSetupWizard() throws UiObjectNotFoundException {
        UiScrollable pager = new UiScrollable(new UiSelector().resourceId(
                "cn.nubia.setupwizard:id/welcome_viewpager"));
        assertTrue(pager.waitForExists(15 * 60 * 1000));

        pager.setAsHorizontalList();
        pager.scrollToEnd(4);

        UiObject finish = new UiObject(new UiSelector().resourceId(
                "cn.nubia.setupwizard:id/btFinish"));
        if (finish.exists()) {
            finish.clickAndWaitForNewWindow();
        }
    }
}
