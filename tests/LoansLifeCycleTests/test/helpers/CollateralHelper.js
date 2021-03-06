const Helper = require('./Helper.js');
const loanHelper = require('./LoanHelper.js');
const api = require('./api.js');
const BN = web3.utils.BN;

function bn (number) {
    if (!(number instanceof String)) {
        number.toString();
    }
    return new BN(number);
}

function divceil (x, y) {
    if (x.mod(y).eq(bn(0))) {
        return x.div(y);
    } else {
        return x.div(y).add(bn(1));
    }
}

const WEI = bn(10).pow(bn(18));
const BASE = bn(10000);

class EntryBuilder {
    constructor (creator, auxToken) {
        this.oracle = { address: Helper.address0x };
        // Loan
        this.loanId = undefined;
        this.loanData = undefined;
        // this.loanAmount = rand(1, 200000000);
        this.loanAmount = '100000000000000000000';
        this.loanAmountRcn = this.loanAmount;
        this.expirationDelta = bn(1000);
        this.durationDelta = bn(1000);

        // Installments
        this.cuota = '10000000000000000000';
        this.punInterestRate = '1555200000000';
        this.installments = '12';
        this.duration = '2592000';
        this.timeUnit = '2592000';
        this.callback = '0x0000000000000000000000000000000000000000';
        // const oracle = '0x0000000000000000000000000000000000000000';
        this.expiration = '1578571215';

        // To oracle
        this.oracleData = [];
        this.tokens = WEI;
        this.equivalent = WEI;
        // To converter
        this.rateFromRCN = WEI;
        this.rateToRCN = WEI;
        // Entry
        this.createFrom = creator;
        this.burnFee = bn(1000);
        this.rewardFee = bn(1000);
        this.liquidationRatio = bn(15000);
        this.balanceRatio = bn(20000);
        this.collateralToken = auxToken;
    }

    with (attr, value) {
        this[attr] = value;
        return this;
    }

    async build (rcn, converter, model, loanManager, debtEngine, collateral, borrower, creator) {
        if (rcn.address !== this.collateralToken.address) {
            await converter.setRate(rcn.address, this.collateralToken.address, this.rateFromRCN);
            await converter.setRate(this.collateralToken.address, rcn.address, this.rateToRCN);
        }

        const salt = bn(web3.utils.randomHex(32));
        // const now = bn(await Helper.getBlockTime());
        // const expiration = now.add(this.expirationDelta);
        // const duration = now.add(this.durationDelta);

        if (this.loanId === undefined) {
            // Brodcast transaction to the network -Request Loan  and  Calculate the Id of the loan with helper function
            const result = await loanHelper.requestLoan(model, borrower, salt, loanManager, debtEngine, creator,
                this.cuota, this.punInterestRate, this.installments, this.duration, this.timeUnit, this.loanAmount,
                this.oracle.address, this.callback, this.expiration);
            this.loanId = result.id;
            this.loanData = result.loanData;

            if (this.oracle.address !== Helper.address0x) {
                this.oracleData = await this.oracle.encodeRate(this.tokens, this.equivalent);
                this.loanAmountRcn = await this.currencyToRCN();
            }
            if (this.onlyTakeALoan) {
                return this.loanId;
            }
        }

        if (this.entryAmount === undefined) {
            const loanAmountInColl = await this.RCNToCollateral(this.loanAmountRcn, converter, this.collateralToken, rcn);
            const minEntryAmount = divceil(loanAmountInColl.mul(this.balanceRatio.add(BASE)), BASE);
            const entryAmount = minEntryAmount * 1.2;
            this.entryAmount = bn(entryAmount.toString());
        }

        this.id = await collateral.getEntriesLength();
        await this.collateralToken.setBalance(creator, this.entryAmount);
        await this.collateralToken.approve(collateral.address, this.entryAmount, { from: creator });

        await collateral.create(
            this.loanId,                  // debtId
            this.oracle.address,
            this.collateralToken.address, // token
            this.entryAmount,             // amount
            this.liquidationRatio,        // liquidationRatio
            this.balanceRatio,            // balanceRatio
            this.burnFee,                 // burnFee
            this.rewardFee,               // rewardFee
            { from: this.createFrom }     // sender
        );

        return this;
    }

    totalFee () {
        return this.burnFee.add(this.rewardFee);
    }

    toRewardFee (amount) {
        return amount.mul(BASE.add(this.rewardFee)).div(BASE).sub(amount);
    }

    toBurnFee (amount) {
        return amount.mul(BASE.add(this.burnFee)).div(BASE).sub(amount);
    }

    withFee (amount) {
        return this.toRewardFee(amount).add(this.toBurnFee(amount)).add(amount);
    }

    async currencyToRCN (amount = this.loanAmount) {
        return this.oracle.getReturn(amount, this.oracleData);
    }

    async collateralToRCN (amount = this.entryAmount, converter, auxToken, rcn) {
        return converter.getReturn(auxToken.address, rcn.address, amount);
    }

    async RCNToCollateral (amount, converter, auxToken, rcn) {
        return converter.getReturn(rcn.address, auxToken.address, amount);
    }
}

const roundCompare = function (x, y) {
    const z = x.sub(y).abs();
    assert.isTrue(z.gte(bn(0)) || z.lte(bn(2)),
        'Diff between ' +
        x.toString() +
        ' to ' +
        y.toString() +
        ' should be less than 1 and is ' +
        z.toString()
    );
};

const checkCollateral = async function (collateral, entryId) {
    const apiCollateral = (await api.getCollateralByEntryId(entryId)).content;
    const ethCollateral = await collateral.entries(entryId);

    // const ethStarted = await collateral.debtToEntry(ethCollateral.debtId);

    assert.equal(apiCollateral.id, entryId, 'Id not equal');
    assert.equal(apiCollateral.debt_id, ethCollateral.debtId, 'Debt not equal');
    assert.equal(apiCollateral.oracle, ethCollateral.oracle, 'Oracle not equal');
    assert.equal(apiCollateral.token, ethCollateral.token, 'token not equal');
    assert.equal(apiCollateral.amount, ethCollateral.amount.toString(), 'amount not equal');
    assert.equal(apiCollateral.liquidation_ratio, ethCollateral.liquidationRatio, 'liquidationRatio not equal');
    assert.equal(apiCollateral.balance_ratio, ethCollateral.balanceRatio, 'Balance ratio not equal');
    assert.equal(apiCollateral.burn_fee, ethCollateral.burnFee, 'burn fee not equal');
    assert.equal(apiCollateral.reward_fee, ethCollateral.rewardFee, 'Reward fee not equal');
    // assert.equal(apiCollateral.started, ethStarted !== undefined);
};

module.exports = {
    roundCompare: roundCompare,
    EntryBuilder: EntryBuilder,
    checkCollateral: checkCollateral,
};
