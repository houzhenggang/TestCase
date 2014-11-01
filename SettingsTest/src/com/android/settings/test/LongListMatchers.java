package com.android.settings.test;

import static com.google.android.apps.common.testing.ui.espresso.matcher.PreferenceMatchers.withKey;
import static com.google.common.base.Preconditions.checkNotNull;

import org.hamcrest.Description;
import org.hamcrest.Matcher;

import android.preference.Preference;

import com.google.android.apps.common.testing.ui.espresso.matcher.BoundedMatcher;

public final class LongListMatchers {

    public static Matcher<Object> withPreferenceKey(final Matcher<Preference> preferenceMatcher) {
        checkNotNull(preferenceMatcher);
        return new BoundedMatcher<Object, Preference>(Preference.class) {

            @Override
            public void describeTo(Description description) {
                description.appendText("with preference key: ");
                preferenceMatcher.describeTo(description);
            }

            @Override
            protected boolean matchesSafely(Preference pref) {
                return preferenceMatcher.matches(pref);
            }
        };
    }

    public static Matcher<Object> withPreferenceKey(String expectedText) {
        checkNotNull(expectedText);
        return withPreferenceKey(withKey(expectedText));
    }
}
