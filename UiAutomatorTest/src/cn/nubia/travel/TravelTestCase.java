package cn.nubia.travel;

import java.io.BufferedReader;
import java.io.File;
import java.io.IOException;
import java.io.InputStreamReader;

import android.widget.Button;
import android.widget.FrameLayout;
import android.widget.LinearLayout;
import android.widget.ListView;

import com.android.uiautomator.core.UiCollection;
import com.android.uiautomator.core.UiObject;
import com.android.uiautomator.core.UiObjectNotFoundException;
import com.android.uiautomator.core.UiSelector;
import com.android.uiautomator.testrunner.UiAutomatorTestCase;

public class TravelTestCase extends UiAutomatorTestCase {

    private String packageName;

    private int number;

    @Override
    protected void setUp() throws Exception {
        super.setUp();
        packageName = "com.android.contacts";
        system("am start --user 0 -W -a android.intent.action.MAIN -c android.intent.category.LAUNCHER -n com.android.contacts/.activities.PeopleActivity");
        sleep(3000);
    }

    public void test() throws UiObjectNotFoundException {
        takeScreenshot();
        tarvel();
        //getUiDevice().dumpWindowHierarchy("/data/local/tmp/xxx.xml");
        //UiObject content = new UiObject(new UiSelector().resourceId("android:id/content"));
        //travel(content);
    }

    /*private void travel(UiObject obj) throws UiObjectNotFoundException {
        for (int i = 0; i < obj.getChildCount(); i++) {
            UiObject child = obj.getChild(new UiSelector().instance(i));
            if (child.exists()) {
                System.out.println(child.getClassName() + " " + child.getBounds());
                if (child.getChildCount() > 0) {
                    travel(child);
                } else {
                    
                }
            }
        }
    }*/

    private void tarvel() throws UiObjectNotFoundException {
        UiCollection content = new UiCollection(new UiSelector().resourceId("android:id/content"));
        UiSelector clickable = new UiSelector().clickable(true);

        int count = content.getChildCount(clickable);
        UiObject[] clickables = new UiObject[count];
        for (int i = 0; i < count; i++) {
            clickables[i] = content.getChildByInstance(clickable, i);
        }

        for (UiObject obj : clickables) {
            if (obj.exists()) {
                if (obj.getClassName().equals(LinearLayout.class.getName())
                        || obj.getClassName().equals(ListView.class.getName())
                        || obj.getClassName().equals(FrameLayout.class.getName())
                        || obj.getClassName().equals(Button.class.getName())) {
                    continue;
                }
                String last = getLastDisplayed();
                if (obj.clickAndWaitForNewWindow()) {
                    String newLast = getLastDisplayed();
                    if (packageName.equals(getUiDevice().getCurrentPackageName()) && !newLast.equals(last)) {
                        UiObject parent = new UiObject(new UiSelector().resourceId("android:id/parentPanel"));
                        if (parent.exists()) {
                            getUiDevice().pressBack();
                            return;
                        } else {
                            takeScreenshot();
                            tarvel();
                        }
                    } else {
                        getUiDevice().pressBack();
                    }
                } else {
                    System.out.println("false");
                }
            }
        }

        UiObject up = new UiObject(new UiSelector().resourceId("android:id/up"));
        if (up.exists()) {
            up.click();
        } else {
            getUiDevice().pressBack();
        }
    }

    private void takeScreenshot() {
        File dir = new File("/data/local/tmp", packageName);
        if (!dir.exists()) {
            dir.mkdir();
        }
        getUiDevice().takeScreenshot(new File(dir, ++number + ".png"));
    }

    private String getLastDisplayed() {
        String result = "";
        try {
            Process p = Runtime.getRuntime().exec("logcat -d -s ActivityManager:I I:s");
            p.waitFor();
            BufferedReader br = new BufferedReader(new InputStreamReader(p.getInputStream()));
            String line = null;
            while ((line = br.readLine()) != null) {
                if (line.indexOf(": Displayed") > -1) {
                    result = line;
                }
            }
        } catch (IOException e) {
            e.printStackTrace();
        } catch (InterruptedException e) {
            e.printStackTrace();
        }
        return result;
    }

    private void system(String cmd) {
        try {
            Process p = Runtime.getRuntime().exec(cmd);
            p.waitFor();
        } catch (IOException e) {
            e.printStackTrace();
        } catch (InterruptedException e) {
            e.printStackTrace();
        }
    }
}
