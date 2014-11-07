package com.ztemt.test.monitor;

import android.app.ActionBar;
import android.app.Activity;
import android.app.Fragment;
import android.app.FragmentTransaction;
import android.app.ActionBar.Tab;
import android.content.Context;
import android.os.Bundle;
import android.view.Menu;
import android.view.MenuInflater;
import android.view.MenuItem;

import com.ztemt.test.monitor.sensor.SensorActivity;
import com.ztemt.test.monitor.sensor.SensorClickListener;

public class TabControl extends Activity {

    @Override
    public void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);

        ActionBar actionBar = getActionBar();
        actionBar.setNavigationMode(ActionBar.NAVIGATION_MODE_TABS);
        actionBar.setDisplayShowTitleEnabled(true);

        Tab tab = actionBar.newTab().setText("Sensor").setTabListener(
                new TabListener<SensorActivity>(this, "Sensor",
                        SensorActivity.class));
        actionBar.addTab(tab);
    }

    /**
     * Load the options menu (defined in xml)
     */
    @Override
    public boolean onCreateOptionsMenu(Menu menu) {
        MenuInflater inflater = getMenuInflater();
        inflater.inflate(R.menu.hardwaremonitor_menu, menu);

        return super.onCreateOptionsMenu(menu);
    }

    /**
     * Defines what occurs when the user selects one of the menu options.
     */
    @Override
    public boolean onOptionsItemSelected(MenuItem item) {
        switch (item.getItemId()) {
        case R.id.exit:
            SensorClickListener.clearAllListeners(this);
            //SensorUtilityFunctions.writeToLogFile("", false);
            finish();
            return true;
        default:
            return super.onOptionsItemSelected(item);
        }
    }

    private static class TabListener<T extends Fragment> implements
            ActionBar.TabListener {
        private Fragment mFragment;
        private Context mContext;
        private String mTag;
        private Class<T> mFragmentClass;

        /**
         * Constructor used each time a new tab is created.
         * 
         * @param context
         *            The host Activity, used to instantiate the fragment
         * @param tag
         *            The identifier tag for the fragment
         * @param fragmentClass
         *            The fragment's class, used to instantiate the fragment
         */
        public TabListener(Context context, String tag, Class<T> fragmentClass) {
            mContext = context;
            mTag = tag;
            mFragmentClass = fragmentClass;
        }

        @Override
        public void onTabReselected(Tab tab, FragmentTransaction ft) {
        }

        @Override
        public void onTabSelected(Tab tab, FragmentTransaction ft) {
            if (mFragment == null) {
                mFragment = Fragment.instantiate(mContext, mFragmentClass.getName());
                ft.add(android.R.id.content, mFragment, mTag);
            }
        }

        @Override
        public void onTabUnselected(Tab tab, FragmentTransaction ft) {
            if (mFragment != null) {
                ft.detach(mFragment);
            }
        }
    }
}
