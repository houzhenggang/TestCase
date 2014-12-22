package com.android.systemui;

import android.os.RemoteException;

import com.ztemt.test.automator.AutomatorTestCase;

public class SleepWakeupTestCase extends AutomatorTestCase {

    public void testSleep() throws RemoteException {
        getUiDevice().sleep();
    }

    public void testWakeup() throws RemoteException {
        getUiDevice().wakeUp();
    }
}
