package cn.nubia.systemupdate;

import android.widget.Button;
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

        String cmd = "am start --activity-clear-task -n cn.nubia.systemupdate/.SystemUpdateActivity";
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

            UiObject confirm = new UiObject(new UiSelector().className(
                    Button.class).text("继续"));
            if (confirm.exists()) {
                confirm.click();
            }

            UiObject select = new UiObject(new UiSelector().className(
                    TextView.class).text("从其它位置选择"));
            if (select.exists()) {
                select.click();

                UiObject myfile = new UiObject(new UiSelector().className(
                        TextView.class).text("我的文件"));
                if (myfile.waitForExists(3000)) {
                    myfile.click();
                }
    
                UiObject storage = new UiObject(new UiSelector().className(
                        TextView.class).text("手机存储"));
                if (storage.waitForExists(3000)) {
                    storage.click();
                }
    
                UiScrollable fileList = new UiScrollable(new UiSelector().scrollable(true));
                if (fileList.waitForExists(3000)) {
                    UiObject update = fileList.getChildByText(new UiSelector().className(
                            TextView.class), "update.zip");
                    if (update.exists()) {
                        update.click();
                    }
                }
            }

            UiObject start = new UiObject(new UiSelector().className(
                    Button.class).text("开始升级"));
            if (start.waitForExists(3000)) {
                start.click();
            }

            UiObject ok = new UiObject(new UiSelector().className(
                    Button.class).text("确定"));
            if (ok.exists()) {
                ok.click();
            }
        }
    }
}
