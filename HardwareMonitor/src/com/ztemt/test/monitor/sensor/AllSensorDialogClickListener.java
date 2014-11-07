package com.ztemt.test.monitor.sensor;

import java.util.List;

import android.content.Context;

public class AllSensorDialogClickListener extends SensorClickListener {

    public AllSensorDialogClickListener(Context context) {
        super(context, null, null);
        mActiveDialog = new SensorStreamRateDialog(context, this, -1);
        mActiveDialog.show();
    }

    /**
     * Sets the streaming rate for all public Android-API sensors.
     * 
     * @param rate 0-3 reserved for pre-defined rates; desired delay between events (microsecond)
     */
    protected void setStreamRate(int rate) {
        List<SensorListItem> sensorList = SensorListItem.getSensorList();
        for (SensorListItem sensorItem : sensorList) {
            SensorListItemView sensorListItemView = SensorListItemView.getSensorListItemView(sensorItem);
            setSensorStreamRate(rate, sensorItem, sensorListItemView, mSensorManager, mActiveDialog);
        }

        mActiveDialog.dismiss();
    }
}
