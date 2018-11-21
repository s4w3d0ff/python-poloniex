import poloniex
import unittest


class TestPolo(unittest.TestCase):

    def test_method_integrity(self):
        self.polo = poloniex.Poloniex()
        for command in poloniex.PUBLIC_COMMANDS:
            self.assertTrue(hasattr(self.polo, command))
        for command in poloniex.PRIVATE_COMMANDS:
            self.assertTrue(hasattr(self.polo, command))
        self.assertTrue(hasattr(self.polo, 'marketTradeHist'))

    def test_coach_existance(self):
        self.polo = poloniex.Poloniex()
        # coach is created by default
        self.assertTrue(isinstance(self.polo.coach, poloniex.Coach))
        # remove coach
        self.polo = poloniex.Poloniex(coach=False)
        self.assertFalse(self.polo.coach)
        # coach injection
        myCoach = poloniex.Coach()
        self.polo = poloniex.Poloniex(coach=myCoach)
        self.polo2 = poloniex.Poloniex(coach=myCoach)
        self.assertTrue(self.polo.coach is self.polo2.coach)

    def test_PoloniexErrors(self):
        self.polo = poloniex.Poloniex()
        # no keys, private command
        with self.assertRaises(poloniex.PoloniexError):
            self.polo.returnBalances()
        # invalid command
        with self.assertRaises(poloniex.PoloniexError):
            self.polo('foo')
        # catch errors returned from poloniex.com
        with self.assertRaises(poloniex.PoloniexError):
            self.polo.returnOrderBook(currencyPair='atestfoo')


if __name__ == '__main__':
    unittest.main()
