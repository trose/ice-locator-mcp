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
  GetStreamingDistributionRequest,
  GetStreamingDistributionResult,
} from "../models/models_1";
export { __MetadataBearer, $Command };
export interface GetStreamingDistributionCommandInput
  extends GetStreamingDistributionRequest {}
export interface GetStreamingDistributionCommandOutput
  extends GetStreamingDistributionResult,
    __MetadataBearer {}
export declare class GetStreamingDistributionCommand extends $Command<
  GetStreamingDistributionCommandInput,
  GetStreamingDistributionCommandOutput,
  CloudFrontClientResolvedConfig
> {
  readonly input: GetStreamingDistributionCommandInput;
  static getEndpointParameterInstructions(): EndpointParameterInstructions;
  constructor(input: GetStreamingDistributionCommandInput);
  resolveMiddleware(
    clientStack: MiddlewareStack<ServiceInputTypes, ServiceOutputTypes>,
    configuration: CloudFrontClientResolvedConfig,
    options?: __HttpHandlerOptions
  ): Handler<
    GetStreamingDistributionCommandInput,
    GetStreamingDistributionCommandOutput
  >;
  private serialize;
  private deserialize;
}
