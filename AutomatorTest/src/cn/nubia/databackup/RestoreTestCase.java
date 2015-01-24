package cn.nubia.databackup;

import android.widget.Button;
import android.widget.LinearLayout;
import android.widget.TextView;

import com.android.uiautomator.core.UiObject;
import com.android.uiautomator.core.UiObjectNotFoundException;
import com.android.uiautomator.core.UiScrollable;
import com.android.uiautomator.core.UiSelector;
import com.ztemt.test.automator.AutomatorTestCase;

public class RestoreTestCase extends AutomatorTestCase {

    @Override
    protected void setUp() throws Exception {
        super.setUp();

        String cmd1 = "am start --activity-clear-task -n cn.nubia.databackup/.ui.MainActivity";
        Process p1 = Runtime.getRuntime().exec(cmd1);
        p1.waitFor();
        String cmd2 = "am start --activity-clear-task -n cn.nubia.databackup/.ui.LauncherActivity";
        Process p2 = Runtime.getRuntime().exec(cmd2);
        p2.waitFor();

        sleep(3000);
    }

    public void testRestore() throws UiObjectNotFoundException {
        UiObject title = new UiObject(new UiSelector().text("还原"));
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

            UiObject confirm = new UiObject(new UiSelector().className(
                    Button.class).text("确定"));
            if (confirm.exists()) {
                confirm.click();
            }

            UiObject loading = new UiObject(new UiSelector().resourceId(
                    "cn.nubia.databackup:id/loading_text"));
            assertTrue("Unable to load backup", loading.waitUntilGone(600000));

            UiObject success = new UiObject(new UiSelector().resourceId(
                    "cn.nubia.databackup:id/restore_result_title"));
            assertTrue("Unable to restore", success.waitForExists(600000));
        }
    }
}
