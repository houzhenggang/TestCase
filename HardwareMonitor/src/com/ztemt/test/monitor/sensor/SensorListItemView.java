package com.ztemt.test.monitor.sensor;

import java.text.DecimalFormat;
import java.util.HashMap;
import android.annotation.SuppressLint;
import android.content.Context;
import android.view.LayoutInflater;
import android.view.View;
import android.view.View.OnClickListener;
import android.widget.Button;
import android.widget.LinearLayout;
import android.widget.TextView;
import com.ztemt.test.monitor.R;

public class SensorListItemView extends LinearLayout implements OnClickListener {

    static private HashMap<SensorListItem, SensorListItemView> sItemViews;

    static {
        sItemViews = new HashMap<SensorListItem, SensorListItemView>();
    }

    static public SensorListItemView getSensorListItemView(SensorListItem listItem) {
        return sItemViews.get(listItem);
    }

    private SensorListItem mListItem;
    private View mChildView;
    // Whether this view is "rolled-up" (ie. just sensor name is visible)
    private boolean mVisible;

    @SuppressLint("InflateParams")
    public SensorListItemView(Context context, SensorListItem listItem) {
        super(context);

        mListItem = listItem;
        mVisible = true;

        LayoutInflater inflater = (LayoutInflater) context.getSystemService(Context.LAYOUT_INFLATER_SERVICE);
        mChildView = inflater.inflate(R.layout.sensor_list_item, null);

        Button viewChartButton = (Button) mChildView.findViewById(R.id.view_chart_button);
        viewChartButton.setOnClickListener(new SensorClickListener(context, listItem, this));

        Button setListenerButton = (Button) mChildView.findViewById(R.id.set_listener_button);
        setListenerButton.setOnClickListener(new SensorClickListener(context, listItem, this));

        Button removeListenerButton = (Button) mChildView.findViewById(R.id.remove_listener_button);
        removeListenerButton.setOnClickListener(new SensorClickListener(context, listItem, this));

        TextView titleView = (TextView) mChildView.findViewById(R.id.sensor_title);
        titleView.setOnClickListener(this);
        titleView.setText(listItem.getTitle());

        addView(mChildView);
        updateView();

        sItemViews.put(listItem, this);
    }

    /**
     * The components of the view that may require updating when sensor data changes, or other events occur.
     */
    public void updateView() {
        TextView streamRateView = (TextView) mChildView.findViewById(R.id.stream_rate);
        streamRateView.setText(getContext().getString(R.string.stream_rate)
                + SensorUtilityFunctions.streamRateString(mListItem.getStreamRate())
                + "(" + new DecimalFormat("#.##").format(SensorUtilityFunctions
                .effectiveStreamRate(mListItem)) + ")");
        streamRateView.setVisibility(mVisible ? VISIBLE : GONE);

        TextView dataView = (TextView) mChildView.findViewById(R.id.sensor_data);
        dataView.setText(SensorUtilityFunctions.getDataString(mListItem));
        dataView.setVisibility(mVisible ? VISIBLE : GONE);

        Button setListenerButton = (Button) mChildView.findViewById(
                R.id.set_listener_button);
        setListenerButton.setVisibility(mVisible ? VISIBLE : GONE);

        Button removeListenerButton = (Button) mChildView.findViewById(
                R.id.remove_listener_button);
        Button viewChartButton = (Button) mChildView.findViewById(
                R.id.view_chart_button);
        if (mListItem.getStreamRate() == -1 && mVisible) {
            removeListenerButton.setVisibility(INVISIBLE);
            viewChartButton.setVisibility(INVISIBLE);
        } else if (!mVisible) {
            removeListenerButton.setVisibility(GONE);
            viewChartButton.setVisibility(GONE);
        } else {
            removeListenerButton.setVisibility(VISIBLE);
            viewChartButton.setVisibility(VISIBLE);
        }

        invalidate();
    }

    /**
     * The click listener for when the name/type of a sensor is "clicked".
     * The result being that the other details are "rolled-up", in order to
     * save screen real-estate.
     */
    @Override
    public void onClick(View v) {
        if (v.getId() == R.id.sensor_title) {
            updateView();
        }
    }
}
