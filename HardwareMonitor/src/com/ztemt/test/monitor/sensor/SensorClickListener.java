package com.ztemt.test.monitor.sensor;

import java.util.HashMap;
import java.util.Iterator;
import java.util.Map.Entry;

import android.content.Context;
import android.content.Intent;
import android.hardware.SensorManager;
import android.os.Handler;
import android.view.View;
import android.view.View.OnClickListener;
import android.widget.EditText;
import android.widget.Toast;

import com.ztemt.test.monitor.R;

public class SensorClickListener implements OnClickListener {

    static protected HashMap<SensorListItem, SensorStreamEventListener> sListeners;

    static {
        sListeners = new HashMap<SensorListItem, SensorStreamEventListener>();
    }

    /**
     * Unregisters all sensor listeners, and resets each sensor's streaming rate
     * @param context
     */
    static public void clearAllListeners(Context context) {
        SensorManager sensorMgr = (SensorManager) context.getSystemService(Context.SENSOR_SERVICE);
        for (Iterator<Entry<SensorListItem, SensorStreamEventListener>> it =
            sListeners.entrySet().iterator(); it.hasNext();) {
            HashMap.Entry<SensorListItem, SensorStreamEventListener> pair = 
                (HashMap.Entry<SensorListItem, SensorStreamEventListener>) it.next();

            sensorMgr.unregisterListener(pair.getValue(), pair.getKey().getSensor());
            pair.getKey().setStreamRate(-1);
            pair.getValue().getItemView().updateView();
        }
    }

    static public void updateListItemView(SensorListItem listItem, SensorListItemView view) {
        SensorStreamEventListener ssel = sListeners.get(listItem);
        if (ssel != null) {
            ssel.setItemView(view);
        }
    }

    private Context mContext;
    private Handler mHandler = new Handler();
    protected SensorManager mSensorManager;

    // The item associated with this dialog/listener
    private SensorListItem mSensorListItem;
    // If available, the view for the list item
    private SensorListItemView mItemView;
    // The dialog that is now active
    protected SensorStreamRateDialog mActiveDialog;

    public SensorClickListener(Context context, SensorListItem sensorListItem, SensorListItemView itemView) {
        mContext = context;
        mSensorManager = (SensorManager) context.getSystemService(Context.SENSOR_SERVICE);
        mSensorListItem = sensorListItem;
        mActiveDialog = null;
        mItemView = itemView;
    }

    @Override
    public void onClick(View v) {
        switch (v.getId()) {
        case R.id.view_chart_button:
            viewSensorDataChart();
            break;
        case R.id.view_stat_button:
            viewSensorDataStat();
            break;
        case R.id.set_listener_button:
            mActiveDialog = new SensorStreamRateDialog(mContext, this,
                    mSensorListItem.getStreamRate());
            mActiveDialog.show();
            break;
        case R.id.remove_listener_button:
            setStreamRate(-1);
            break;
        case R.id.delay_button_normal:
            setStreamRate(SensorManager.SENSOR_DELAY_NORMAL);
            setStreamTimer();
            break;
        case R.id.delay_button_ui:
            setStreamRate(SensorManager.SENSOR_DELAY_UI);
            setStreamTimer();
            break;
        case R.id.delay_button_game:
            setStreamRate(SensorManager.SENSOR_DELAY_GAME);
            setStreamTimer();
            break;
        case R.id.delay_button_fastest:
            setStreamRate(SensorManager.SENSOR_DELAY_FASTEST);
            setStreamTimer();
            break;
        case R.id.delay_button_submit:
            EditText rateField = (EditText) mActiveDialog.findViewById(R.id.delay_rate_field);

            try {
                int rate = Integer.parseInt(rateField.getText().toString());
                setStreamRate(rate);
                setStreamTimer();
            } catch (NumberFormatException e) {
                Toast.makeText(mContext, "Invalid number entry", Toast.LENGTH_LONG).show();
            }
            break;
        case R.id.delay_button_cancel:
            mActiveDialog.cancel();
            break;
        }
    }

    /**
     * Sets the streaming rate for the applicable sensor, and updates the screen
     */
    protected void setStreamRate(int rate) {
        setSensorStreamRate(rate, mSensorListItem, mItemView, mSensorManager, mActiveDialog);
    }

    protected void viewSensorDataChart() {
        Intent intent = new Intent(mContext, SensorChartActivity.class);
        intent.putExtra("type", mSensorListItem.getSensorType());
        intent.putExtra("title", mSensorListItem.getTitle());
        intent.putExtra("unit", mSensorListItem.getSensorUnit());
        intent.putExtra("max_x", mSensorListItem.getSensorChartMaxX());
        intent.putExtra("min_y", mSensorListItem.getSensorChartMinY());
        intent.putExtra("max_y", mSensorListItem.getSensorChartMaxY());
        mContext.startActivity(intent);
    }

    protected void viewSensorDataStat() {
        Intent intent = new Intent(mContext, SensorDataStatActivity.class);
        intent.putExtra("title", mSensorListItem.getSensorName());
        intent.putExtra("type", mSensorListItem.getSensorType());
        mContext.startActivity(intent);
    }

    protected void setStreamTimer() {
        EditText timerField = (EditText) mActiveDialog.findViewById(R.id.timer_field);
        int millis = -1;

        try {
            millis = Integer.parseInt(timerField.getText().toString());
        } catch (NumberFormatException e) {
            // Invalid number entry
        }

        if (millis >= 0) {
            mHandler.postDelayed(new Runnable() {
                @Override
                public void run() {
                    setStreamRate(-1);
                }
            }, millis);
        }
    }

    /**
     * Sets the sensor stream rate
     * 
     * @param rate 0-3 reserved for pre-defined rates; desired delay between events (microsecond)
     * @param sensorListItem List item (wrapper) for sensor
     * @param itemView View (if available) for sensor list item
     * @param sensorManager The sensor manager to register/remove the listener from
     * @param activeDialog The dialog box that led to here (to be closed)
     */
    public static void setSensorStreamRate(int rate, SensorListItem sensorListItem, SensorListItemView itemView,
            SensorManager sensorManager, SensorStreamRateDialog activeDialog) {
        if (rate == sensorListItem.getStreamRate()) {
            if (activeDialog != null) {
                activeDialog.dismiss();
            }
            return;
        } else if (rate == -1) {
            SensorStreamEventListener ssel = sListeners.remove(sensorListItem);
            if (ssel == null) {
                return;
            }
            sensorManager.unregisterListener(ssel, sensorListItem.getSensor());
            sensorListItem.closeLogWriter();
        } else {
            SensorStreamEventListener oldSSEL = sListeners.remove(sensorListItem);
            if (oldSSEL != null) {
                sensorManager.unregisterListener(oldSSEL, sensorListItem.getSensor());
            }

            SensorStreamEventListener ssel = new SensorStreamEventListener(sensorListItem, itemView);
            if (!sensorManager.registerListener(ssel, sensorListItem.getSensor(), rate)) {
                rate = -1;
            } else {
                sListeners.put(sensorListItem, ssel);
                sensorListItem.createLogWriter();
            }
            activeDialog.dismiss();
        }

        sensorListItem.setStreamRate(rate);
        if (itemView != null) {
            itemView.updateView();
        }
    }
}
