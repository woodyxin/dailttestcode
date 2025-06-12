def coinexchange(coins,amount):
    """
    Function to find the minimum number of coins needed to make a given amount.

    :param coins: List of coin denominations
    :param amount: The total amount to be made with the coins
    :return: Minimum number of coins needed, or -1 if it's not possible
    """
    dp = [float('inf')] * (amount + 1)
    dp[0] = 0

    for coin in coins:
        for x in range(coin, amount + 1):
            dp[x] = min(dp[x], dp[x - coin] + 1)

    return dp[amount] if dp[amount] != float('inf') else -1