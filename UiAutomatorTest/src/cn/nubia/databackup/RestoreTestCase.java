package cn.nubia.databackup;

import android.widget.LinearLayout;
import android.widget.TextView;

import com.android.uiautomator.core.UiObject;
import com.android.uiautomator.core.UiObjectNotFoundException;
import com.android.uiautomator.core.UiScrollable;
import com.android.uiautomator.core.UiSelector;
import com.android.uiautomator.testrunner.UiAutomatorTestCase;

public class RestoreTestCase extends UiAutomatorTestCase {

    @Override
    protected void setUp() throws Exception {
        super.setUp();

        String cmd = "am start --activity-clear-task -n cn.nubia.databackup/.ui.MainActivity";
        Process p = Runtime.getRuntime().exec(cmd);
        p.waitFor();

        sleep(3000);
    }

    public void testRestore() throws UiObjectNotFoundException {
        UiObject title = new UiObject(new UiSelector().resourceId(
                "cn.nubia.databackup:id/title").text("还原"));
        title.clickAndWaitForNewWindow();

        UiScrollable list = new UiScrollable(new UiSelector().resourceId(
                "cn.nubia.databackup:id/restore_listview"));
        UiObject restore = list.getChild(new UiSelector().className(
                LinearLayout.class).index(0).childSelector(new UiSelector()
                .resourceId("cn.nubia.databackup:id/restore")));
        if (restore.exists()) {
            UiObject button = restore.getChild(new UiSelector().className(
                    TextView.class).text("还原"));
            button.clickAndWaitForNewWindow();

            UiObject loading = new UiObject(new UiSelector().resourceId(
                    "cn.nubia.databackup:id/loading_text"));
            assertTrue("Unable to load backup", loading.waitUntilGone(600000));

            UiObject success = new UiObject(new UiSelector().resourceId(
                    "cn.nubia.databackup:id/restore_result_title"));
            assertTrue("Unable to restore", success.waitForExists(600000));
        }
    }
}
