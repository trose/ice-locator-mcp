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
  GetDistributionConfigRequest,
  GetDistributionConfigResult,
} from "../models/models_1";
export { __MetadataBearer, $Command };
export interface GetDistributionConfigCommandInput
  extends GetDistributionConfigRequest {}
export interface GetDistributionConfigCommandOutput
  extends GetDistributionConfigResult,
    __MetadataBearer {}
export declare class GetDistributionConfigCommand extends $Command<
  GetDistributionConfigCommandInput,
  GetDistributionConfigCommandOutput,
  CloudFrontClientResolvedConfig
> {
  readonly input: GetDistributionConfigCommandInput;
  static getEndpointParameterInstructions(): EndpointParameterInstructions;
  constructor(input: GetDistributionConfigCommandInput);
  resolveMiddleware(
    clientStack: MiddlewareStack<ServiceInputTypes, ServiceOutputTypes>,
    configuration: CloudFrontClientResolvedConfig,
    options?: __HttpHandlerOptions
  ): Handler<
    GetDistributionConfigCommandInput,
    GetDistributionConfigCommandOutput
  >;
  private serialize;
  private deserialize;
}
