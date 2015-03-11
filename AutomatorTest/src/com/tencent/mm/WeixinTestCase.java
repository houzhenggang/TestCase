package com.tencent.mm;

import android.widget.Button;
import android.widget.ImageView;
import android.widget.ListView;
import android.widget.TextView;

import com.android.uiautomator.core.UiObject;
import com.android.uiautomator.core.UiObjectNotFoundException;
import com.android.uiautomator.core.UiScrollable;
import com.android.uiautomator.core.UiSelector;
import com.ztemt.test.automator.AutomatorTestCase;

public class WeixinTestCase extends AutomatorTestCase {

    @Override
    protected void setUp() throws Exception {
        super.setUp();

        String cmd = "am start --activity-clear-task -n com.tencent.mm/.ui.LauncherUI";
        Process p = Runtime.getRuntime().exec(cmd);
        p.waitFor();
    }

    public void testLogin() throws UiObjectNotFoundException {
        UiObject validation = new UiObject(new UiSelector().packageName(
                "com.tencent.mm"));
        assertTrue(validation.waitForExists(5000));

        UiScrollable listview = new UiScrollable(new UiSelector().className(ListView.class));
        if (listview.waitForExists(3000)) {
            return;
        }

        UiObject switchAccount = new UiObject(new UiSelector().text("切换帐号"));
        if (switchAccount.exists()) {
            switchAccount.click();

            UiObject accountType = new UiObject(new UiSelector().textContains("微信号"));
            accountType.click();
        } else {
            UiObject image = new UiObject(new UiSelector().className(
                    ImageView.class).index(0));
            image.waitUntilGone(30000);
    
            UiObject confirm = new UiObject(new UiSelector().className(
                    Button.class).text("确定"));
            if (confirm.exists()) {
                confirm.click();
            }
    
            UiObject login = new UiObject(new UiSelector().className(
                    Button.class).text("登录"));
            login.clickAndWaitForNewWindow();
    
            UiObject otherWay = new UiObject(new UiSelector().className(
                    TextView.class).text("使用其他方式登录"));
            otherWay.clickAndWaitForNewWindow();
        }

        UiObject username = new UiObject(new UiSelector().className(
                TextView.class).text("帐   号").fromParent(
                new UiSelector().index(1)));
        username.setText("test9094");
        UiObject password = new UiObject(new UiSelector().className(
                TextView.class).text("密   码").fromParent(
                new UiSelector().index(1)));
        password.setText("ztemt123");
        UiObject loginbtn = new UiObject(new UiSelector().className(
                Button.class).text("登录"));
        loginbtn.click();

        UiObject ok = new UiObject(new UiSelector().className(
                Button.class).textMatches("^(确定|否)$"));
        if (ok.waitForExists(8000)) {
            ok.click();
        }
    }
}
