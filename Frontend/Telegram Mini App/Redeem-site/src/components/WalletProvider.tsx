"use client";

import { AptosWalletAdapterProvider } from "@aptos-labs/wallet-adapter-react";
import { PetraWallet } from "petra-plugin-wallet-adapter";

import { PropsWithChildren } from "react";
import { Network } from "@aptos-labs/ts-sdk";
import {  useAutoConnect } from "./AutoConnectProvider";


export const WalletProvider = ({ children }: PropsWithChildren) => {
  const { autoConnect } = useAutoConnect();

  const wallets = [
    new PetraWallet(),
  
  ];

  return (
    <AptosWalletAdapterProvider
      autoConnect={autoConnect}
      plugins={wallets}
      dappConfig={{
        network: Network.TESTNET,
        mizuwallet: {
          manifestURL:
            "https://assets.mz.xyz/static/config/mizuwallet-connect-manifest.json",
        },
      }}
      onError={(error) => {
        console.log(error);
      }}
    >
      {children}
    </AptosWalletAdapterProvider>
  );
};
