package com.ztemt.test.monitor.sensor;

import android.app.Dialog;
import android.content.Context;
import android.view.View;
import android.widget.Button;
import android.widget.EditText;

import com.ztemt.test.monitor.R;

public class SensorStreamRateDialog extends Dialog {

    public SensorStreamRateDialog(Context context, View.OnClickListener onClickListener,
            int currentStreamRate) {
        super(context);

        setContentView(R.layout.stream_rate_dialog);
        setTitle("Sensor Stream Rate");

        String currentRate = currentStreamRate == -1 ? "" : String.valueOf(currentStreamRate);
        EditText rateField = (EditText) findViewById(R.id.delay_rate_field);
        rateField.setText(currentRate);

        Button delayNormalButton = (Button) findViewById(R.id.delay_button_normal);
        delayNormalButton.setOnClickListener(onClickListener);

        Button delayUIButton = (Button) findViewById(R.id.delay_button_ui);
        delayUIButton.setOnClickListener(onClickListener);

        Button delayGameButton = (Button) findViewById(R.id.delay_button_game);
        delayGameButton.setOnClickListener(onClickListener);

        Button delayFastestButton = (Button) findViewById(R.id.delay_button_fastest);
        delayFastestButton.setOnClickListener(onClickListener);

        Button dialogSubmitButton = (Button) findViewById(R.id.delay_button_submit);
        dialogSubmitButton.setOnClickListener(onClickListener);

        Button dialogCancelButton = (Button) findViewById(R.id.delay_button_cancel);
        dialogCancelButton.setOnClickListener(onClickListener);
    }
}
