package com.android.settings.test;

import static com.android.settings.test.LongListMatchers.withPreferenceKey;
import static com.google.android.apps.common.testing.ui.espresso.Espresso.onData;
import static com.google.android.apps.common.testing.ui.espresso.Espresso.onView;
import static com.google.android.apps.common.testing.ui.espresso.action.ViewActions.click;
import static com.google.android.apps.common.testing.ui.espresso.assertion.ViewAssertions.matches;
import static com.google.android.apps.common.testing.ui.espresso.matcher.ViewMatchers.isChecked;
import static com.google.android.apps.common.testing.ui.espresso.matcher.ViewMatchers.isFocusable;
import static com.google.android.apps.common.testing.ui.espresso.matcher.ViewMatchers.withClassName;
import static com.google.android.apps.common.testing.ui.espresso.matcher.ViewMatchers.withId;
import static com.google.android.apps.common.testing.ui.espresso.matcher.ViewMatchers.withText;
import static org.hamcrest.Matchers.allOf;
import static org.hamcrest.Matchers.containsString;
import static org.hamcrest.Matchers.endsWith;
import static org.hamcrest.Matchers.not;
import android.test.ActivityInstrumentationTestCase2;

import com.google.android.apps.common.testing.ui.espresso.DataInteraction;

@SuppressWarnings({ "unchecked", "rawtypes" })
public class DevelopmentSettingsTestCase extends ActivityInstrumentationTestCase2 {

    private static final String LAUNCHER_ACTIVITY = "com.android.settings.DevelopmentSettings";
    private static Class sActivityClass;

    static {
        try {
            sActivityClass = Class.forName(LAUNCHER_ACTIVITY);
        } catch (ClassNotFoundException e) {
            throw new RuntimeException(e);
        }
    }

    public DevelopmentSettingsTestCase() {
        super(sActivityClass);
    }

    @Override
    protected void setUp() throws Exception {
        super.setUp();
        getActivity();
    }

    public void testKeepScreenIsChecked() {
        onData(withPreferenceKey("keep_screen_on"))
                .inAdapterView(allOf(withId(android.R.id.list), isFocusable()))
                .onChildView(withClassName(endsWith("NubiaSwitch")))
                .check(matches(not(isChecked()))).perform(click())
                .check(matches(isChecked()));
    }

    public void testTrackFrameTimeIsDumpsysGfxinfo() {
        String expectedText = "adb shell dumpsys gfxinfo";
        DataInteraction trackFrameTime = onData(
                withPreferenceKey("track_frame_time")).inAdapterView(
                allOf(withId(android.R.id.list), isFocusable()));
        trackFrameTime.perform(click());
        onView(withText(containsString(expectedText))).perform(click());
        trackFrameTime.onChildView(withId(android.R.id.summary)).check(
                matches(withText(containsString(expectedText))));
    }
}
