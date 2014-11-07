package com.ztemt.test.monitor.sensor;

import android.app.Activity;
import android.os.Bundle;
import android.view.Menu;
import android.view.MenuInflater;
import android.view.MenuItem;

import com.ztemt.test.monitor.R;
import com.ztemt.test.monitor.chart.AxisLineChart;
import com.ztemt.test.monitor.sensor.SensorStreamEventListener.SensorChangedListener;

public class SensorChartActivity extends Activity implements SensorChangedListener {

    private AxisLineChart mChart;
    private String mType;
    private boolean mPaused = false;
    private boolean mDisableUIDataUpdate;

    public void onSensorChanged(String type, float data0, float data1, float data2) {
        if (!mPaused && type.equals(mType)) {
            mChart.update(new double[] { data0, data1, data2 });
        }
    }

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);

        String title = getIntent().getStringExtra("title");
        String unit = getIntent().getStringExtra("unit");
        double maxX = getIntent().getDoubleExtra("max_x", 2000.0);
        double minY = getIntent().getDoubleExtra("min_y", 0.0);
        double maxY = getIntent().getDoubleExtra("max_y", 50.0);
        mType = getIntent().getStringExtra("type");

        mDisableUIDataUpdate = SensorStreamEventListener.sDisableUIDataUpdate;
        mChart = new AxisLineChart(this, title, unit, maxX, minY, maxY, 3);
        setContentView(mChart.getView());
    }

    @Override
    protected void onResume() {
        super.onResume();
        SensorStreamEventListener.sDisableUIDataUpdate = true;
        SensorStreamEventListener.setListener(this);
    }

    @Override
    protected void onPause() {
        super.onPause();
        SensorStreamEventListener.sDisableUIDataUpdate = mDisableUIDataUpdate;
        SensorStreamEventListener.setListener(null);
    }

    @Override
    public boolean onCreateOptionsMenu(Menu menu) {
        MenuInflater inflater = getMenuInflater();
        inflater.inflate(R.menu.chart_menu, menu);

        return super.onCreateOptionsMenu(menu);
    }

    @Override
    public boolean onOptionsItemSelected(MenuItem item) {
        switch (item.getItemId()) {
        case R.id.chart_data_update_toggle:
            mPaused = !mPaused;
            item.setTitle(mPaused ? "Enable Chart Update" : "Disable Chart Update");
            return true;
        default:
            return super.onOptionsItemSelected(item);
        }
    }

    @Override
    public void onBackPressed() {
        new Thread() {
            public void run() {
                mPaused = true;
            }
        }.start();
        super.onBackPressed();
    }
}
