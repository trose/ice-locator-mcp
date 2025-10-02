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
  GetDistributionRequest,
  GetDistributionResult,
} from "../models/models_1";
export { __MetadataBearer, $Command };
export interface GetDistributionCommandInput extends GetDistributionRequest {}
export interface GetDistributionCommandOutput
  extends GetDistributionResult,
    __MetadataBearer {}
export declare class GetDistributionCommand extends $Command<
  GetDistributionCommandInput,
  GetDistributionCommandOutput,
  CloudFrontClientResolvedConfig
> {
  readonly input: GetDistributionCommandInput;
  static getEndpointParameterInstructions(): EndpointParameterInstructions;
  constructor(input: GetDistributionCommandInput);
  resolveMiddleware(
    clientStack: MiddlewareStack<ServiceInputTypes, ServiceOutputTypes>,
    configuration: CloudFrontClientResolvedConfig,
    options?: __HttpHandlerOptions
  ): Handler<GetDistributionCommandInput, GetDistributionCommandOutput>;
  private serialize;
  private deserialize;
}
