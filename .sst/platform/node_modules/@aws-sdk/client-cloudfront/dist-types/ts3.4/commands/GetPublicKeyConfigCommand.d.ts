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
import {
  GetPublicKeyConfigRequest,
  GetPublicKeyConfigResult,
} from "../models/models_1";
export { __MetadataBearer, $Command };
export interface GetPublicKeyConfigCommandInput
  extends GetPublicKeyConfigRequest {}
export interface GetPublicKeyConfigCommandOutput
  extends GetPublicKeyConfigResult,
    __MetadataBearer {}
export declare class GetPublicKeyConfigCommand extends $Command<
  GetPublicKeyConfigCommandInput,
  GetPublicKeyConfigCommandOutput,
  CloudFrontClientResolvedConfig
> {
  readonly input: GetPublicKeyConfigCommandInput;
  static getEndpointParameterInstructions(): EndpointParameterInstructions;
  constructor(input: GetPublicKeyConfigCommandInput);
  resolveMiddleware(
    clientStack: MiddlewareStack<ServiceInputTypes, ServiceOutputTypes>,
    configuration: CloudFrontClientResolvedConfig,
    options?: __HttpHandlerOptions
  ): Handler<GetPublicKeyConfigCommandInput, GetPublicKeyConfigCommandOutput>;
  private serialize;
  private deserialize;
}
