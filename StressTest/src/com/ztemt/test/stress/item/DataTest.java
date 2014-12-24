package com.ztemt.test.stress.item;

import java.lang.reflect.Method;

import android.content.Context;
import android.net.ConnectivityManager;
import android.net.wifi.WifiManager;
import android.telephony.PhoneStateListener;
import android.telephony.TelephonyManager;
import android.util.Log;

import com.ztemt.test.stress.R;

public class DataTest extends BaseTest {

    private static final String LOG_TAG = "DataTest";

    private TelephonyManager mTM;

    private ConnectivityManager mCM;
    private WifiManager mWM;

    private PhoneStateListener mPhoneStateListener = new PhoneStateListener() {

        @Override
        public void onDataConnectionStateChanged(int state, int networkType) {
            if (state == TelephonyManager.DATA_CONNECTED) {
                mTM.listen(mPhoneStateListener, LISTEN_NONE);
                setSuccess();
                resume();
            }
        }
    };

    public DataTest(Context context) {
        super(context);

        mTM = (TelephonyManager) mContext.getSystemService(Context.TELEPHONY_SERVICE);
        mCM = (ConnectivityManager) mContext.getSystemService(Context.CONNECTIVITY_SERVICE);
        mWM = (WifiManager) mContext.getSystemService(Context.WIFI_SERVICE);
    }

    @Override
    public void onRun() {
        if (mWM.isWifiEnabled()) {
            mWM.setWifiEnabled(false);
        }

        if (getMobileDataEnabled()) {
            setMobileDataEnabled(false);
            sleep(3000);
        }
        setMobileDataEnabled(true);
        setTimeout(120000);
        mTM.listen(mPhoneStateListener, PhoneStateListener.LISTEN_DATA_CONNECTION_STATE);
        pause();
        mTM.listen(mPhoneStateListener, PhoneStateListener.LISTEN_NONE);
    }

    @Override
    public String getTitle() {
        return mContext.getString(R.string.data_test);
    }

    @Override
    public void setFailure() {
        super.setFailure();
        Log.e(LOG_TAG, "data state isn't connected");
        sleep(10000);
    }

    private boolean getMobileDataEnabled() {
        try {
            Method m = ConnectivityManager.class.getMethod("getMobileDataEnabled");
            return (Boolean) m.invoke(mCM);
        } catch (Exception e) {
            Log.e(LOG_TAG, e.getMessage(), e);
            return false;
        }
    }

    private void setMobileDataEnabled(boolean enabled) {
        try {
            Method m = ConnectivityManager.class.getMethod(
                    "setMobileDataEnabled", Boolean.TYPE);
            m.invoke(mCM, enabled);
        } catch (Exception e) {
            Log.e(LOG_TAG, e.getMessage(), e);
        }
    }
}
