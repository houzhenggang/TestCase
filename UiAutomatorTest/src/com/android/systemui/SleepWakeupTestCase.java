package com.android.systemui;

import android.os.RemoteException;

import com.android.uiautomator.testrunner.UiAutomatorTestCase;

public class SleepWakeupTestCase extends UiAutomatorTestCase {

    public void testSleep() throws RemoteException {
        getUiDevice().sleep();
    }

    public void testWakeup() throws RemoteException {
        getUiDevice().wakeUp();
    }
}
