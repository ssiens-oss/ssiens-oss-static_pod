/**
 * Budget guard - hard stop on AI costs
 * Prevents runaway spending
 */

let spent = 0;
const DAILY = Number(process.env.AI_BUDGET_DAILY_USD || 5);

module.exports = {
  check(cost) {
    if (spent + cost > DAILY) {
      throw new Error(`AI budget exceeded: $${spent.toFixed(2)}/$${DAILY.toFixed(2)}`);
    }
    spent += cost;
  },

  get() {
    return {
      spent: Number(spent.toFixed(4)),
      limit: DAILY,
      remaining: Number((DAILY - spent).toFixed(4))
    };
  },

  reset() {
    spent = 0;
  }
};
