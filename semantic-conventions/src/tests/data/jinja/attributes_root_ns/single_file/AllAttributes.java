package io.opentelemetry.instrumentation.api.semconv;

class AllAttributes {
  class FirstAttributes {
    /**
    * short description of attr_one
    */
    public static final AttributeKey<Boolean> FIRST_ATTR_ONE = booleanKey("first.attr_one");

    /**
    * short description of attr_one_a
    */
    public static final AttributeKey<Long> FIRST_ATTR_ONE_A = longKey("first.attr_one_a");

    /**
    * this is the description of attribute template
    */
    public static final AttributeKeyTemplate<String> FIRST_ATTR_TEMPLATE_ONE = stringKey("first.attr_template_one");
  }
  class SecondAttributes {
    /**
    * short description of attr_two
    */
    public static final AttributeKey<String> SECOND_ATTR_TWO = stringKey("second.attr_two");
  }
  class ThirdAttributes {
    /**
    * this is the description of attribute template
    */
    public static final AttributeKeyTemplate<String> THIRD_ATTR_TEMPLATE_THREE = stringKey("third.attr_template_three");

    /**
    * short description of attr_three
    */
    public static final AttributeKey<String> THIRD_ATTR_THREE = stringKey("third.attr_three");
  }
  /**
  * short description of attr_four
  */
  public static final AttributeKey<String> ATTR_FOUR = stringKey("attr_four");
}