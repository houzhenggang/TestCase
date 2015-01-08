package cn.nubia.systemupdate;

import android.widget.ScrollView;
import android.widget.TextView;

import com.android.uiautomator.core.UiObject;
import com.android.uiautomator.core.UiObjectNotFoundException;
import com.android.uiautomator.core.UiScrollable;
import com.android.uiautomator.core.UiSelector;
import com.ztemt.test.automator.AutomatorTestCase;

public class SystemUpdateTestCase extends AutomatorTestCase {

    @Override
    protected void setUp() throws Exception {
        super.setUp();

        String cmd = "am start -n cn.nubia.systemupdate/.SystemUpdateActivity";
        Process p = Runtime.getRuntime().exec(cmd);
        p.waitFor();

        sleep(3000);
    }

    public void testLocalUpdate() throws UiObjectNotFoundException {
        UiScrollable list = new UiScrollable(new UiSelector().className(
                ScrollView.class));
        UiObject local = list.getChildByText(new UiSelector().className(
                TextView.class), "本地安装包更新");
        if (local.exists()) {
            local.clickAndWaitForNewWindow();

            UiObject start = new UiObject(new UiSelector().resourceId(
                    "cn.nubia.systemupdate:id/sdcard_update_btn"));
            if (start.exists()) {
                start.click();
            }
        }
    }
}
