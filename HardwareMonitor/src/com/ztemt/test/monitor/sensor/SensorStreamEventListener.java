package com.ztemt.test.monitor.sensor;

import java.util.Calendar;

import android.hardware.Sensor;
import android.hardware.SensorEvent;
import android.hardware.SensorEventListener;

/*
 * Race conditions are not a concern within these functions, as they are all processed within
 * the same thread that registered the listener. In this case, the UI thread. Most of the
 * latency caused by each event is due to the view update.
 */
public class SensorStreamEventListener implements SensorEventListener {

    //private static final String TAG = "SensorStreamEventListener";
    // How often to update views; .1 -> once event 10ms
    private static final double VIEW_UPDATE_RATE = .1;
    // If ture -> do not refresh UI to show streaming sensor data
    public static boolean sDisableUIDataUpdate = false;
    
    private SensorListItem mSensorListItem;
    private SensorListItemView mItemView;
    private long mLastSCTimestamp;
    private long mLastACTimestamp;

    public SensorStreamEventListener(SensorListItem sensorListItem, SensorListItemView itemView) {
        mSensorListItem = sensorListItem;
        mItemView = itemView;
        mLastSCTimestamp = 0;
        mLastACTimestamp = 0;
    }

    public void setItemView(SensorListItemView itemView) {
        mItemView = itemView;
    }

    public SensorListItemView getItemView() {
        return mItemView;
    }

    @Override
    public void onAccuracyChanged(Sensor sensor, int accuracy) {
        mSensorListItem.setAccuracy(accuracy);

        // To avoid redrawing the screen too frequently, we limit the total number of updates per second,
        // based on the number of sensors currently streaming
        long currentTimestamp = Calendar.getInstance().getTime().getTime();
        if (!sDisableUIDataUpdate && currentTimestamp > mLastACTimestamp
                        + SensorClickListener.sListeners.size()
                        / VIEW_UPDATE_RATE) {
            mItemView.updateView();
            mLastACTimestamp = currentTimestamp;
        }
    }

    @Override
    public void onSensorChanged(SensorEvent event) {
        mSensorListItem.setData(event.values[0], event.values[1], event.values[2],
                event.accuracy, event.timestamp);

        // To avoid redrawing the screen too frequently, we limit the total number of updates per second,
        // based on the number of sensors currently streaming
        long currentTimestamp = Calendar.getInstance().getTime().getTime();
        if (!sDisableUIDataUpdate && currentTimestamp > mLastSCTimestamp
                + SensorClickListener.sListeners.size() / VIEW_UPDATE_RATE) {
            mItemView.updateView();
            mLastSCTimestamp = currentTimestamp;
        }

        if (sListener != null) {
            sListener.onSensorChanged(mSensorListItem.getSensorType(), event.values[0],
                    event.values[1], event.values[2]);
        }
    }

    interface SensorChangedListener {
        public void onSensorChanged(String type, float data0, float data1, float data2);
    }

    static SensorChangedListener sListener;

    static void setListener(SensorChangedListener listener) {
        sListener = listener;
    }
}
