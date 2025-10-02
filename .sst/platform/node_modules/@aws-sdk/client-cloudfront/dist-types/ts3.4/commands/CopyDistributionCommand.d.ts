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
  CopyDistributionRequest,
  CopyDistributionResult,
} from "../models/models_0";
export { __MetadataBearer, $Command };
export interface CopyDistributionCommandInput extends CopyDistributionRequest {}
export interface CopyDistributionCommandOutput
  extends CopyDistributionResult,
    __MetadataBearer {}
export declare class CopyDistributionCommand extends $Command<
  CopyDistributionCommandInput,
  CopyDistributionCommandOutput,
  CloudFrontClientResolvedConfig
> {
  readonly input: CopyDistributionCommandInput;
  static getEndpointParameterInstructions(): EndpointParameterInstructions;
  constructor(input: CopyDistributionCommandInput);
  resolveMiddleware(
    clientStack: MiddlewareStack<ServiceInputTypes, ServiceOutputTypes>,
    configuration: CloudFrontClientResolvedConfig,
    options?: __HttpHandlerOptions
  ): Handler<CopyDistributionCommandInput, CopyDistributionCommandOutput>;
  private serialize;
  private deserialize;
}
