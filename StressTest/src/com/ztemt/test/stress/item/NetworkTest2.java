package com.ztemt.test.stress.item;

import android.annotation.TargetApi;
import android.content.Context;
import android.content.Intent;
import android.os.Build;
import android.provider.Settings;
import android.telephony.PhoneStateListener;
import android.telephony.ServiceState;
import android.telephony.TelephonyManager;
import android.util.Log;

import com.ztemt.test.stress.R;

public class NetworkTest2 extends BaseTest {

    private static final String LOG_TAG = "NetworkTest2";

    private TelephonyManager mTM;

    private PhoneStateListener mPhoneStateListener = new PhoneStateListener() {

        @Override
        public void onServiceStateChanged(ServiceState serviceState) {
            int state = serviceState.getState();

            if (state == ServiceState.STATE_IN_SERVICE) {
                mTM.listen(this, LISTEN_NONE);
                setSuccess();
                resume();
            }
        }
    };

    public NetworkTest2(Context context) {
        super(context);

        mTM = (TelephonyManager) context.getSystemService(Context.TELEPHONY_SERVICE);
    }

    @Override
    public void onRun() {
        if (!isAirplaneModeOn()) {
            setAirplaneModeOn(true);
        }
        sleep(30000);
        setAirplaneModeOn(false);
        setTimeout(60000);
        mTM.listen(mPhoneStateListener, PhoneStateListener.LISTEN_SERVICE_STATE);
        pause();
        mTM.listen(mPhoneStateListener, PhoneStateListener.LISTEN_NONE);
    }

    @Override
    public String getTitle() {
        return mContext.getString(R.string.network_test2);
    }

    @Override
    public void setFailure() {
        super.setFailure();
        Log.e(LOG_TAG, "network state isn't in service");
        sleep(10000);
    }

    @SuppressWarnings("deprecation")
    @TargetApi(Build.VERSION_CODES.JELLY_BEAN_MR1)
    private void setAirplaneModeOn(boolean enabling) {
        int mode = enabling ? 1 : 0;
        if (Build.VERSION.SDK_INT < 17) {
            Settings.System.putInt(mContext.getContentResolver(),
                    Settings.System.AIRPLANE_MODE_ON, mode);
        } else {
            Settings.Global.putInt(mContext.getContentResolver(),
                    Settings.Global.AIRPLANE_MODE_ON, mode);
        }
        Intent intent = new Intent(Intent.ACTION_AIRPLANE_MODE_CHANGED);
        intent.putExtra("state", enabling);
        mContext.sendBroadcast(intent);
    }

    @SuppressWarnings("deprecation")
    @TargetApi(Build.VERSION_CODES.JELLY_BEAN_MR1)
    private boolean isAirplaneModeOn() {
        int mode;
        if (Build.VERSION.SDK_INT < 17) {
            mode = Settings.System.getInt(mContext.getContentResolver(),
                    Settings.System.AIRPLANE_MODE_ON, 0);
        } else {
            mode = Settings.Global.getInt(mContext.getContentResolver(),
                    Settings.Global.AIRPLANE_MODE_ON, 0);
        }
        return mode == 1;
    }
}
