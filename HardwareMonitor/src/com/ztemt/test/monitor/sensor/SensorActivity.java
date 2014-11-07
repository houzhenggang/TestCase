package com.ztemt.test.monitor.sensor;

import android.app.Fragment;
import android.os.Bundle;
import android.view.LayoutInflater;
import android.view.Menu;
import android.view.MenuInflater;
import android.view.MenuItem;
import android.view.View;
import android.view.ViewGroup;

import com.ztemt.test.monitor.R;

public class SensorActivity extends Fragment {

    private SensorListView mListView;
    private MenuItem mUpdateUIMenuItem;

    @Override
    public View onCreateView(LayoutInflater inflater, ViewGroup container,
            Bundle savedInstanceState) {
        if (mListView == null) {
            mListView = new SensorListView(getActivity());
        }

        setHasOptionsMenu(true);

        return mListView;
    }

    /**
     * Load the options menu (defined in xml)
     */
    @Override
    public void onCreateOptionsMenu(Menu menu, MenuInflater inflater) {
        inflater.inflate(R.menu.streaming_menu, menu);

        mUpdateUIMenuItem = menu.findItem(R.id.ui_data_update_toggle);
        mUpdateUIMenuItem.setTitle(SensorStreamEventListener.sDisableUIDataUpdate
                ? "Enable Screen Update" : "Disable Screen Update");
    }

    /**
     * Defines what occurs when the user selects one of the menu options.
     */
    @Override
    public boolean onOptionsItemSelected(MenuItem item) {
        switch (item.getItemId()) {
        case R.id.all_listeners_add:
            new AllSensorDialogClickListener(getActivity());
            return true;
        case R.id.all_listeners_remove:
            SensorClickListener.clearAllListeners(getActivity());
            return true;
        case R.id.ui_data_update_toggle:
            SensorStreamEventListener.sDisableUIDataUpdate = !SensorStreamEventListener.sDisableUIDataUpdate;
            mUpdateUIMenuItem.setTitle(SensorStreamEventListener.sDisableUIDataUpdate
                    ? "Enable Screen Update" : "Disable Screen Update");
            return true;
        default:
            return super.onOptionsItemSelected(item);
        }
    }
}
