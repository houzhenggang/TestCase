package cn.nubia.calculator2.preset.test;

import static com.google.android.apps.common.testing.ui.espresso.Espresso.onView;
import static com.google.android.apps.common.testing.ui.espresso.action.ViewActions.click;
import static com.google.android.apps.common.testing.ui.espresso.assertion.ViewAssertions.matches;
import static com.google.android.apps.common.testing.ui.espresso.matcher.ViewMatchers.withId;
import static com.google.android.apps.common.testing.ui.espresso.matcher.ViewMatchers.withText;

import android.content.res.Resources;
import android.test.ActivityInstrumentationTestCase2;
import android.test.suitebuilder.annotation.LargeTest;

@LargeTest
@SuppressWarnings({ "unchecked", "rawtypes" })
public class CalculatorTestCase extends ActivityInstrumentationTestCase2 {

    private static final String LAUNCHER_ACTIVITY = "cn.nubia.calculator2.Calculator";
    private static Class sActivityClass;

    static {
        try {
            sActivityClass = Class.forName(LAUNCHER_ACTIVITY);
        } catch (ClassNotFoundException e) {
            throw new RuntimeException(e);
        }
    }

    private int mDigit1;
    private int mDigit2;
    private int mDigit3;
    private int mDigit4;
    private int mDigit5;
    private int mDigit6;
    private int mDigit7;
    private int mDigit8;
    private int mDigit9;
    private int mDigit0;
    private int mDot;
    private int mPlus;
    private int mMinus;
    private int mMul;
    private int mDiv;
    private int mEqual;
    private int mClear;
    private int mResult;

    public CalculatorTestCase() {
        super(sActivityClass);
    }

    @Override
    protected void setUp() throws Exception {
        super.setUp();
        Resources res = getActivity().getResources();
        mDigit1 = res.getIdentifier("digit1", "id", "cn.nubia.calculator2.preset");
        mDigit2 = res.getIdentifier("digit2", "id", "cn.nubia.calculator2.preset");
        mDigit3 = res.getIdentifier("digit3", "id", "cn.nubia.calculator2.preset");
        mDigit4 = res.getIdentifier("digit4", "id", "cn.nubia.calculator2.preset");
        mDigit5 = res.getIdentifier("digit5", "id", "cn.nubia.calculator2.preset");
        mDigit6 = res.getIdentifier("digit6", "id", "cn.nubia.calculator2.preset");
        mDigit7 = res.getIdentifier("digit7", "id", "cn.nubia.calculator2.preset");
        mDigit8 = res.getIdentifier("digit8", "id", "cn.nubia.calculator2.preset");
        mDigit9 = res.getIdentifier("digit9", "id", "cn.nubia.calculator2.preset");
        mDigit0 = res.getIdentifier("digit0", "id", "cn.nubia.calculator2.preset");
        mDot    = res.getIdentifier("dot", "id", "cn.nubia.calculator2.preset");
        mPlus   = res.getIdentifier("plus", "id", "cn.nubia.calculator2.preset");
        mMinus  = res.getIdentifier("minus", "id", "cn.nubia.calculator2.preset");
        mMul    = res.getIdentifier("mul", "id", "cn.nubia.calculator2.preset");
        mDiv    = res.getIdentifier("div", "id", "cn.nubia.calculator2.preset");
        mEqual  = res.getIdentifier("equal", "id", "cn.nubia.calculator2.preset");
        mClear  = res.getIdentifier("clear", "id", "cn.nubia.calculator2.preset");
        mResult = res.getIdentifier("cal_txt2", "id", "cn.nubia.calculator2.preset");
    }

    public void testIntegerPlus() {
        onView(withId(mClear)).perform(click());
        onView(withId(mDigit1)).perform(click());
        onView(withId(mDigit2)).perform(click());
        onView(withId(mDigit3)).perform(click());
        onView(withId(mDigit4)).perform(click());
        onView(withId(mDigit5)).perform(click());
        onView(withId(mPlus)).perform(click());
        onView(withId(mDigit6)).perform(click());
        onView(withId(mDigit7)).perform(click());
        onView(withId(mDigit8)).perform(click());
        onView(withId(mDigit9)).perform(click());
        onView(withId(mDigit0)).perform(click());
        onView(withId(mEqual)).perform(click());
        onView(withId(mResult)).check(matches(withText("80,235")));
    }

    public void testIntegerMinus() {
        onView(withId(mClear)).perform(click());
        onView(withId(mDigit1)).perform(click());
        onView(withId(mDigit2)).perform(click());
        onView(withId(mDigit3)).perform(click());
        onView(withId(mDigit4)).perform(click());
        onView(withId(mDigit5)).perform(click());
        onView(withId(mMinus)).perform(click());
        onView(withId(mDigit6)).perform(click());
        onView(withId(mDigit7)).perform(click());
        onView(withId(mDigit8)).perform(click());
        onView(withId(mDigit9)).perform(click());
        onView(withId(mDigit0)).perform(click());
        onView(withId(mEqual)).perform(click());
        onView(withId(mResult)).check(matches(withText("−55,545")));
    }

    public void testIntegerMul() {
        onView(withId(mClear)).perform(click());
        onView(withId(mDigit1)).perform(click());
        onView(withId(mDigit2)).perform(click());
        onView(withId(mDigit3)).perform(click());
        onView(withId(mDigit4)).perform(click());
        onView(withId(mDigit5)).perform(click());
        onView(withId(mMul)).perform(click());
        onView(withId(mDigit6)).perform(click());
        onView(withId(mDigit7)).perform(click());
        onView(withId(mDigit8)).perform(click());
        onView(withId(mDigit9)).perform(click());
        onView(withId(mDigit0)).perform(click());
        onView(withId(mEqual)).perform(click());
        onView(withId(mResult)).check(matches(withText("838,102,050")));
    }

    public void testIntegerDiv() {
        onView(withId(mClear)).perform(click());
        onView(withId(mDigit1)).perform(click());
        onView(withId(mDigit2)).perform(click());
        onView(withId(mDigit3)).perform(click());
        onView(withId(mDigit4)).perform(click());
        onView(withId(mDigit5)).perform(click());
        onView(withId(mDiv)).perform(click());
        onView(withId(mDigit6)).perform(click());
        onView(withId(mDigit7)).perform(click());
        onView(withId(mDigit8)).perform(click());
        onView(withId(mDigit9)).perform(click());
        onView(withId(mDigit0)).perform(click());
        onView(withId(mEqual)).perform(click());
        onView(withId(mResult)).check(matches(withText("0.18183826779")));
    }

    public void testFloatPlus() {
        onView(withId(mClear)).perform(click());
        onView(withId(mDigit0)).perform(click());
        onView(withId(mDot)).perform(click());
        onView(withId(mDigit1)).perform(click());
        onView(withId(mDigit2)).perform(click());
        onView(withId(mDigit3)).perform(click());
        onView(withId(mDigit4)).perform(click());
        onView(withId(mPlus)).perform(click());
        onView(withId(mDigit5)).perform(click());
        onView(withId(mDot)).perform(click());
        onView(withId(mDigit6)).perform(click());
        onView(withId(mDigit7)).perform(click());
        onView(withId(mDigit8)).perform(click());
        onView(withId(mDigit9)).perform(click());
        onView(withId(mEqual)).perform(click());
        onView(withId(mResult)).check(matches(withText("5.8023")));
    }

    public void testFloatMinus() {
        onView(withId(mClear)).perform(click());
        onView(withId(mDigit0)).perform(click());
        onView(withId(mDot)).perform(click());
        onView(withId(mDigit1)).perform(click());
        onView(withId(mDigit2)).perform(click());
        onView(withId(mDigit3)).perform(click());
        onView(withId(mDigit4)).perform(click());
        onView(withId(mMinus)).perform(click());
        onView(withId(mDigit5)).perform(click());
        onView(withId(mDot)).perform(click());
        onView(withId(mDigit6)).perform(click());
        onView(withId(mDigit7)).perform(click());
        onView(withId(mDigit8)).perform(click());
        onView(withId(mDigit9)).perform(click());
        onView(withId(mEqual)).perform(click());
        onView(withId(mResult)).check(matches(withText("−5.5555")));
    }

    public void testFloatMul() {
        onView(withId(mClear)).perform(click());
        onView(withId(mDigit0)).perform(click());
        onView(withId(mDot)).perform(click());
        onView(withId(mDigit1)).perform(click());
        onView(withId(mDigit2)).perform(click());
        onView(withId(mDigit3)).perform(click());
        onView(withId(mDigit4)).perform(click());
        onView(withId(mMul)).perform(click());
        onView(withId(mDigit5)).perform(click());
        onView(withId(mDot)).perform(click());
        onView(withId(mDigit6)).perform(click());
        onView(withId(mDigit7)).perform(click());
        onView(withId(mDigit8)).perform(click());
        onView(withId(mDigit9)).perform(click());
        onView(withId(mEqual)).perform(click());
        onView(withId(mResult)).check(matches(withText("0.70077626")));
    }

    public void testFloatDiv() {
        onView(withId(mClear)).perform(click());
        onView(withId(mDigit0)).perform(click());
        onView(withId(mDot)).perform(click());
        onView(withId(mDigit1)).perform(click());
        onView(withId(mDigit2)).perform(click());
        onView(withId(mDigit3)).perform(click());
        onView(withId(mDigit4)).perform(click());
        onView(withId(mDiv)).perform(click());
        onView(withId(mDigit5)).perform(click());
        onView(withId(mDot)).perform(click());
        onView(withId(mDigit6)).perform(click());
        onView(withId(mDigit7)).perform(click());
        onView(withId(mDigit8)).perform(click());
        onView(withId(mDigit9)).perform(click());
        onView(withId(mEqual)).perform(click());
        onView(withId(mResult)).check(matches(withText("0.0217295603")));
    }

    public void testComplexExpression() {
        onView(withId(mClear)).perform(click());
        onView(withId(mDigit1)).perform(click());
        onView(withId(mDigit2)).perform(click());
        onView(withId(mPlus)).perform(click());
        onView(withId(mDigit3)).perform(click());
        onView(withId(mDigit4)).perform(click());
        onView(withId(mMinus)).perform(click());
        onView(withId(mDigit5)).perform(click());
        onView(withId(mDigit6)).perform(click());
        onView(withId(mMul)).perform(click());
        onView(withId(mDigit7)).perform(click());
        onView(withId(mDigit8)).perform(click());
        onView(withId(mDiv)).perform(click());
        onView(withId(mDigit9)).perform(click());
        onView(withId(mDot)).perform(click());
        onView(withId(mDigit0)).perform(click());
        onView(withId(mEqual)).perform(click());
        onView(withId(mResult)).check(matches(withText("−439.33333333")));
    }
}
