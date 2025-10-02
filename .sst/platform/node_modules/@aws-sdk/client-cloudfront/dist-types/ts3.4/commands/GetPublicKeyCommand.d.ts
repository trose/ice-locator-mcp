import { EndpointParameterInstructions } from "@smithy/middleware-endpoint";
import { Command as $Command } from "@smithy/smithy-client";
import {
  Handler,
  HttpHandlerOptions as __HttpHandlerOptions,
  MetadataBearer as __MetadataBearer,
  MiddlewareStack,
} from "@smithy/types";
import {
  CloudFrontClientResolvedConfig,
  ServiceInputTypes,
  ServiceOutputTypes,
} from "../CloudFrontClient";
import { GetPublicKeyRequest, GetPublicKeyResult } from "../models/models_1";
export { __MetadataBearer, $Command };
export interface GetPublicKeyCommandInput extends GetPublicKeyRequest {}
export interface GetPublicKeyCommandOutput
  extends GetPublicKeyResult,
    __MetadataBearer {}
export declare class GetPublicKeyCommand extends $Command<
  GetPublicKeyCommandInput,
  GetPublicKeyCommandOutput,
  CloudFrontClientResolvedConfig
> {
  readonly input: GetPublicKeyCommandInput;
  static getEndpointParameterInstructions(): EndpointParameterInstructions;
  constructor(input: GetPublicKeyCommandInput);
  resolveMiddleware(
    clientStack: MiddlewareStack<ServiceInputTypes, ServiceOutputTypes>,
    configuration: CloudFrontClientResolvedConfig,
    options?: __HttpHandlerOptions
  ): Handler<GetPublicKeyCommandInput, GetPublicKeyCommandOutput>;
  private serialize;
  private deserialize;
}
