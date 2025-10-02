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
  GetStreamingDistributionConfigRequest,
  GetStreamingDistributionConfigResult,
} from "../models/models_1";
export { __MetadataBearer, $Command };
export interface GetStreamingDistributionConfigCommandInput
  extends GetStreamingDistributionConfigRequest {}
export interface GetStreamingDistributionConfigCommandOutput
  extends GetStreamingDistributionConfigResult,
    __MetadataBearer {}
export declare class GetStreamingDistributionConfigCommand extends $Command<
  GetStreamingDistributionConfigCommandInput,
  GetStreamingDistributionConfigCommandOutput,
  CloudFrontClientResolvedConfig
> {
  readonly input: GetStreamingDistributionConfigCommandInput;
  static getEndpointParameterInstructions(): EndpointParameterInstructions;
  constructor(input: GetStreamingDistributionConfigCommandInput);
  resolveMiddleware(
    clientStack: MiddlewareStack<ServiceInputTypes, ServiceOutputTypes>,
    configuration: CloudFrontClientResolvedConfig,
    options?: __HttpHandlerOptions
  ): Handler<
    GetStreamingDistributionConfigCommandInput,
    GetStreamingDistributionConfigCommandOutput
  >;
  private serialize;
  private deserialize;
}
