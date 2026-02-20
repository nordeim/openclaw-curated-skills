const { AbiCoder } = require('ethers');

const ERROR_SIGNATURES = {
  '0x019ce337': { name: 'AssetUniverseFromTokenNotAllowed', params: ['address'] },
  '0x7110d8d1': { name: 'AssetUniverseToTokenNotAllowed', params: ['address'] },
  '0x7e72157c': { name: 'SlippageFeedMissing', params: ['uint256', 'address'] },
  '0x385c3b50': { name: 'SlippageMinToReceiveTooLow', params: ['uint256', 'uint256', 'uint256'] },
  '0x08066fee': { name: 'StaticAllocationFeedMissing', params: ['address'] },
  '0xf430d069': { name: 'StaticAllocationZeroPortfolioValue', params: [] },
  '0x50361bf4': { name: 'StaticAllocationNoRebalanceTrigger', params: [] },
  '0x5226d958': { name: 'StaticAllocationTokenNotSupported', params: ['address'] },
  '0x4e1aab69': { name: 'StaticAllocationInsufficientBalance', params: ['address', 'uint256', 'uint256'] },
  '0xe5ded9a9': { name: 'StaticAllocationZeroPredictedValue', params: [] },
  '0xa82525ab': { name: 'StaticAllocationOutsideTolerance', params: [] },
  '0x08c379a0': { name: 'Error', params: ['string'] }
};

const coder = new AbiCoder();

function decodeError(errorData) {
  if (!errorData || errorData === '0x') return null;

  const selector = errorData.slice(0, 10);
  const def = ERROR_SIGNATURES[selector];

  if (!def) return `Unknown Error (Selector: ${selector})`;

  try {
    const decoded = coder.decode(def.params, '0x' + errorData.slice(10));
    let message = `Policy Violation: ${def.name}`;

    if (def.name.includes('NotAllowed')) {
      message += `\nToken: ${decoded[0]}`;
    } else if (def.name === 'SlippageMinToReceiveTooLow') {
      message += `\nTrade Index: ${decoded[0]}\nMin To Receive: ${decoded[1]}\nMin Allowed: ${decoded[2]}`;
    } else if (def.name === 'StaticAllocationInsufficientBalance') {
      message += `\nToken: ${decoded[0]}\nRequired: ${decoded[1]}\nAvailable: ${decoded[2]}`;
    } else if (def.name === 'Error') {
      message = `Revert: ${decoded[0]}`;
    }

    return message;
  } catch (e) {
    return `Failed to decode ${def.name}: ${e.message}`;
  }
}

module.exports = { decodeError };
